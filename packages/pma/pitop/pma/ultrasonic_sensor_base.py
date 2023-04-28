import atexit
import logging
import time
from abc import abstractmethod
from collections import deque
from sched import scheduler
from threading import Event, Lock, Thread

import numpy as np
from gpiozero import SmoothedInputDevice

from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.firmware_device import (
    FirmwareDevice,
    PTInvalidFirmwareDeviceException,
)
from pitop.common.singleton import Singleton
from pitop.pma.common.utils import get_pin_for_port

from .common.ultrasonic_registers import (
    UltrasonicConfigSettings,
    UltrasonicRegisters,
    UltrasonicRegisterTypes,
)
from .plate_interface import PlateInterface

logger = logging.getLogger(__name__)


class UltrasonicSensorBase:
    _max_distance = None
    threshold = None

    @property
    def max_distance(self):
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        if value <= 0:
            raise ValueError("invalid maximum distance (must be positive)")
        t = self.threshold_distance
        self._max_distance = value
        self.threshold_distance = t

    @property
    def threshold_distance(self):
        return self.threshold * self.max_distance

    @threshold_distance.setter
    def threshold_distance(self, value):
        self.threshold = value / self.max_distance

    @property
    def distance(self):
        return self.value * self._max_distance

    @abstractmethod
    def in_range(self):
        raise NotImplementedError

    @abstractmethod
    def value(self):
        raise NotImplementedError

    @abstractmethod
    def pin(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def wait_for_active(self, timeout=None):
        raise NotImplementedError

    @abstractmethod
    def wait_for_inactive(self, timeout=None):
        raise NotImplementedError


class CompatibilityCheck(metaclass=Singleton):
    __MIN_FIRMWARE_MAJOR_VERSION = 22

    def __init__(self):
        self.check()

    def check(self):
        try:
            firmware_device = FirmwareDevice(FirmwareDeviceID.pt4_expansion_plate)
            if (
                firmware_device.get_fw_version_major()
                < self.__MIN_FIRMWARE_MAJOR_VERSION
            ):
                raise RuntimeError(
                    "Usage of the analog ports for the Ultrasonic Sensor requires an Expansion Plate with "
                    f"a minimum version version of V{self.__MIN_FIRMWARE_MAJOR_VERSION}. "
                    f"Please update your Expansion Plate firmware to continue."
                )

        except PTInvalidFirmwareDeviceException:
            raise RuntimeError(
                "Please use an Expansion Plate in order to use the analog ports for the Ultrasonic "
                "Sensor."
            )


class UltrasonicSensorMCU(UltrasonicSensorBase):
    __MIN_FIRMWARE_MAJOR_VERSION = 22

    def __init__(
        self, port_name, queue_len, max_distance, threshold_distance, partial, name
    ):
        self._pma_port = port_name
        self.name = name

        # Distance readings
        if max_distance <= 0:
            raise ValueError("invalid maximum distance (must be positive)")
        self._max_distance = max_distance
        self._filtered_distance = max_distance
        self.threshold = threshold_distance / max_distance
        self._data_read_dt = 0.1
        self.__queue_len = queue_len
        self.__data_queue = deque(maxlen=self.__queue_len)

        # MCU configuration
        self.__mcu_device = PlateInterface().get_device_mcu()
        CompatibilityCheck()
        self.__registers = UltrasonicRegisters[self._pma_port]
        self.__configure_mcu()

        # User-programmable callbacks
        self.when_activated = None
        self.when_deactivated = None

        # Data state
        self.__partial = partial
        self.__data_ready = False
        self.__active = True

        # Thread communication
        self.__new_reading_event = Event()
        self.__activated_event = Event()
        self.__deactivated_event = Event()
        self._continue_processing = True

        if self.__partial:
            self.__data_ready = True
        else:
            self.__queue_check = Thread(target=self.__queue_filled_check, daemon=True)
            self.__queue_check.start()

        # Data read loop
        self._read_scheduler = Thread(target=self.__read_scheduler, daemon=True)
        self._read_scheduler.start()

        # Monitor for changes from active to inactive or vice versa
        self.__state_check = Thread(target=self.__state_monitor, daemon=True)
        self.__state_check.start()

        atexit.register(self.close)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._continue_processing = False
        if self._process_image_thread.is_alive():
            self._process_image_thread.join()

    def __configure_mcu(self):
        self.__mcu_device.write_byte(
            self.__registers[UltrasonicRegisterTypes.CONFIG],
            UltrasonicConfigSettings[self._pma_port],
        )

    @property
    def value(self):
        while not self.__data_ready:
            time.sleep(self._data_read_dt)
        return min(1.0, self._filtered_distance / self._max_distance)

    @property
    def pin(self):
        print(
            "An Ultrasonic Sensor connected to an analog port is controlled directly by the MCU and does not have an"
            "associated Raspberry Pi pin. Returning None."
        )
        return None

    def close(self):
        self.__mcu_device.write_byte(
            self.__registers[UltrasonicRegisterTypes.CONFIG], 0x00
        )

    @property
    def in_range(self):
        return not self.__active

    def wait_for_active(self, timeout=None):
        self.__activated_event.wait(timeout=timeout)

    def wait_for_inactive(self, timeout=None):
        self.__deactivated_event.wait(timeout=timeout)

    def __read_scheduler(self):
        s = scheduler(time.time, time.sleep)
        s.enter(self._data_read_dt, 1, self.__read_loop, (s,))
        s.run()

    def __read_loop(self, s):
        self.__data_queue.append(self.__read_distance())
        self._filtered_distance = np.median(self.__data_queue)
        self.__new_reading_event.set()
        self.__new_reading_event.clear()
        if self._continue_processing:
            s.enter(self._data_read_dt, 1, self.__read_loop, (s,))

    def __state_monitor(self):
        while self._continue_processing:
            self.__new_reading_event.wait()
            if self.__data_ready:
                self.__check_for_state_change()

    def __check_for_state_change(self):
        if self.__active and self.__inactive_criteria():
            self.__was_deactivated()
            return
        if not self.__active and self.__active_criteria():
            self.__was_activated()
            return

    def __active_criteria(self):
        return self._filtered_distance >= self.threshold_distance

    def __inactive_criteria(self):
        return not self.__active_criteria()

    def __was_activated(self):
        if callable(self.when_activated):
            self.when_activated()
        self.__active = True
        self.__activated_event.set()
        self.__activated_event.clear()

    def __was_deactivated(self):
        if callable(self.when_deactivated):
            self.when_deactivated()
        self.__active = False
        self.__deactivated_event.set()
        self.__deactivated_event.clear()

    def __queue_filled_check(self):
        while self._continue_processing:
            self.__new_reading_event.wait()
            if self.__queue_len == len(self.__data_queue):
                self.__data_ready = True
                break

    def __read_distance(self):
        distance = (
            self.__mcu_device.read_unsigned_word(
                register_address=self.__registers[UltrasonicRegisterTypes.DATA],
                little_endian=True,
            )
            / 100
        )
        if distance == 0:
            return self._max_distance
        return distance


# Modified version of gpiozero's DistanceSensor class that only uses 1 pin
#
# Note: all private member variables are semi-private to follow upstream gpiozero convention
# and to override inherited functions
class UltrasonicSensorRPI(SmoothedInputDevice, UltrasonicSensorBase):
    ECHO_LOCK = Lock()

    def __init__(
        self,
        port_name,
        queue_len=3,
        max_distance=3,
        threshold_distance=0.3,
        partial=True,
        name="ultrasonic",
    ):
        self._pma_port = port_name
        self.name = name

        SmoothedInputDevice.__init__(
            self,
            get_pin_for_port(self._pma_port),
            pull_up=False,
            queue_len=queue_len,
            sample_wait=0.1,
            partial=partial,
            ignore=frozenset({None}),
        )

        try:
            if max_distance <= 0:
                raise ValueError("invalid maximum distance (must be positive)")
            self._max_distance = max_distance
            self.threshold = threshold_distance / max_distance
            self.speed_of_sound = 343.26  # m/s

            self._echo = Event()
            self._echo_rise = None
            self._echo_fall = None
            self.pin.edges = "both"
            self.pin.bounce = None
            self.pin.when_changed = self._echo_changed
            self._queue.start()
        except Exception:
            self.close()
            raise

    def close(self):
        try:
            super(UltrasonicSensorRPI, self).close()
        except RuntimeError:
            logger.debug(
                f"Ultrasonic Sensor on port {self._pma_port} - "
                "there was an error in closing the port!"
            )

    @property
    def value(self):
        return super(UltrasonicSensorRPI, self).value

    @property
    def pin(self):
        return super(UltrasonicSensorRPI, self).pin

    def _echo_changed(self, ticks, level):
        if level:
            self._echo_rise = ticks
        else:
            self._echo_fall = ticks
            self._echo.set()

    def _read(self):
        # Wait up to 50ms for the echo pin to fall to low (the maximum echo
        # pulse is 35ms so this gives some leeway); if it doesn't something is
        # horribly wrong (most likely at the hardware level)
        if self.pin.state:
            if not self._echo.wait(0.05):
                logger.debug(
                    f"Ultrasonic Sensor on port {self._pma_port} - "
                    "no echo received, not using value"
                )
                return None
        self._echo.clear()
        self._echo_fall = None
        self._echo_rise = None
        # Obtain the class-level ECHO_LOCK to ensure multiple distance sensors
        # don't listen for each other's "pings"
        with UltrasonicSensorRPI.ECHO_LOCK:
            # Wait up to 200ms for the echo pin to rise and fall
            if self._echo.wait(0.2):
                if self._echo_fall is not None and self._echo_rise is not None:
                    distance = (
                        self.pin_factory.ticks_diff(self._echo_fall, self._echo_rise)
                        * self.speed_of_sound
                        / 2.0
                    )
                    return round(min(1.0, distance / self._max_distance), 2)
                else:
                    # If we only saw the falling edge it means we missed
                    # the echo because it was too fast
                    return None
            else:
                # The echo pin never rose or fell - assume that distance is max
                logger.debug(
                    f"Ultrasonic Sensor on port {self._pma_port} - "
                    "no echo received, using max distance "
                )
                return 1.0

    @property
    def in_range(self):
        return not self.is_active
