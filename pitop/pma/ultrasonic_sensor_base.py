from gpiozero import SmoothedInputDevice
from threading import Event, Lock

from pitopcommon.logger import PTLogger

from abc import abstractmethod
from .plate_interface import PlateInterface
from .common.ultrasonic_registers import (
    UltrasonicRegisters,
    UltrasonicRegisterTypes,
    UltrasonicConfigSettings,
)
from pitop.pma.common.utils import get_pin_for_port
import atexit


class UltrasonicSensorBase:
    _max_distance = None
    threshold = None

    @property
    def max_distance(self):
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        if value <= 0:
            raise ValueError('invalid maximum distance (must be positive)')
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
        pass

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def pin(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def wait_for_active(self, timeout=None):
        pass

    @abstractmethod
    def wait_for_inactive(self, timeout=None):
        pass


class UltrasonicSensorMCU(UltrasonicSensorBase):
    def __init__(
            self,
            port_name,
            max_distance=3,
            threshold_distance=0.3,
            name="ultrasonic",
            **_ignored
    ):
        self._pma_port = port_name
        self.name = name

        if max_distance <= 0:
            raise ValueError('invalid maximum distance (must be positive)')
        self._max_distance = max_distance
        self.threshold = threshold_distance / max_distance

        self.__mcu_device = PlateInterface().get_device_mcu()
        self.__registers = UltrasonicRegisters[self._pma_port]

        self.__configure_mcu()

        atexit.register(self.close)

    def __configure_mcu(self):
        self.__mcu_device.write_byte(self.__registers[UltrasonicRegisterTypes.CONFIG],
                                     UltrasonicConfigSettings[self._pma_port]
                                     )

    @property
    def value(self):
        distance_cm = self.__mcu_device.read_unsigned_word(
            register_address=self.__registers[UltrasonicRegisterTypes.DATA],
            little_endian=True
        )
        distance = distance_cm / 100
        return min(1.0, distance / self._max_distance)

    @property
    def pin(self):
        print("An Ultrasonic Sensor connected to an analog port is controlled directly by the MCU and does not have an"
              "associated Raspberry Pi pin. Returning None.")
        return None

    def close(self):
        self.__mcu_device.write_byte(self.__registers[UltrasonicRegisterTypes.CONFIG], 0x00)

    @property
    def in_range(self):
        pass

    def wait_for_active(self, timeout=None):
        pass

    def wait_for_inactive(self, timeout=None):
        pass


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
            name="ultrasonic"
    ):

        self._pma_port = port_name
        self.name = name

        SmoothedInputDevice.__init__(self,
                                     get_pin_for_port(self._pma_port),
                                     pull_up=False,
                                     queue_len=queue_len,
                                     sample_wait=0.1,
                                     partial=partial,
                                     ignore=frozenset({None}),
                                     )

        try:
            if max_distance <= 0:
                raise ValueError('invalid maximum distance (must be positive)')
            self._max_distance = max_distance
            self.threshold = threshold_distance / max_distance
            self.speed_of_sound = 343.26  # m/s

            self._echo = Event()
            self._echo_rise = None
            self._echo_fall = None
            self.pin.edges = 'both'
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
            PTLogger.debug(f"Ultrasonic Sensor on port {self._pma_port} - "
                           "there was an error in closing the port!")

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
                PTLogger.debug(f"Ultrasonic Sensor on port {self._pma_port} - "
                               "no echo received, not using value")
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
                        self.pin_factory.ticks_diff(
                            self._echo_fall, self._echo_rise) *
                        self.speed_of_sound / 2.0)
                    return round(min(1.0, distance / self._max_distance), 2)
                else:
                    # If we only saw the falling edge it means we missed
                    # the echo because it was too fast
                    return None
            else:
                # The echo pin never rose or fell - assume that distance is max
                PTLogger.debug(f"Ultrasonic Sensor on port {self._pma_port} - "
                               "no echo received, using max distance ")
                return 1.0

    @property
    def in_range(self):
        return not self.is_active
