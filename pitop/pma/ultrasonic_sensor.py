from gpiozero import SmoothedInputDevice
from threading import Event, Lock

from pitopcommon.logger import PTLogger

from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma.common.utils import get_pin_for_port, Port
from abc import abstractmethod
from .plate_interface import PlateInterface
from .common.ultrasonic_registers import (
    UltrasonicRegisters,
    UltrasonicRegisterTypes,
    UltrasonicConfigSettings,
)


def UltrasonicSensor(*args, **kwargs):
    def factory(_port_name):
        assert (port_name in Port)
        if port_name in valid_analog_ports:
            return UltrasonicSensorMCU(*args, **kwargs)
        else:
            return UltrasonicSensorRPI(*args, **kwargs)

    valid_analog_ports = ["A1", "A3"]
    if "port_name" in kwargs:
        port_name = kwargs.get("port_name")
    else:
        port_name = args[0]

    return factory(_port_name=port_name)


class UltrasonicSensorBaseClass:
    _max_distance = None
    threshold = None

    @property
    def own_state(self):
        return {
            'distance': self.distance,
        }

    @property
    def max_distance(self):
        """The maximum distance that the sensor will measure in meters.

        This value is specified in the constructor and is used to
        provide the scaling for the :attr:`~SmoothedInputDevice.value`
        attribute. When :attr:`distance` is equal to
        :attr:`max_distance`, :attr:`~SmoothedInputDevice.value` will be
        1.
        """
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
        """
        The distance, measured in meters, that will trigger the
        :attr:`when_in_range` and :attr:`when_out_of_range` events when
        crossed. This is simply a meter-scaled variant of the usual
        :attr:`~SmoothedInputDevice.threshold` attribute.
        """
        return self.threshold * self.max_distance

    @threshold_distance.setter
    def threshold_distance(self, value):
        self.threshold = value / self.max_distance

    @property
    def distance(self):
        """Returns the current distance measured by the sensor in meters.

        Note
        that this property will have a value between 0 and
        :attr:`max_distance`.
        """
        return self.value * self._max_distance

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def pin(self):
        pass

    @abstractmethod
    def close(self):
        pass


class UltrasonicSensorMCU(Stateful, Recreatable, UltrasonicSensorBaseClass):
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

        Stateful.__init__(self)
        Recreatable.__init__(self, {"port_name": port_name,
                                    "name": self.name,
                                    "max_distance": lambda: self.max_distance,
                                    "threshold_distance": lambda: self.threshold_distance})

    def __configure_mcu(self):
        self.__mcu_device.write_byte(self.__registers[UltrasonicRegisterTypes.CONFIG],
                                     UltrasonicConfigSettings[self._pma_port]
                                     )

    @property
    def value(self):
        """Returns a value between 0, indicating that something is either
        touching the sensor or is sufficiently near that the sensor can't tell
        the difference, and 1, indicating that something is at or beyond the
        specified *max_distance*."""
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


# Modified version of gpiozero's DistanceSensor class that only uses 1 pin
#
# Note: all private member variables are semi-private to follow upstream gpiozero convention
# and to override inherited functions
class UltrasonicSensorRPI(Stateful, Recreatable, SmoothedInputDevice, UltrasonicSensorBaseClass):
    ECHO_LOCK = Lock()

    def __init__(
            self,
            port_name,
            queue_len=9,
            max_distance=3,
            threshold_distance=0.3,
            partial=False,
            name="ultrasonic"
    ):

        self._pma_port = port_name
        self.name = name

        SmoothedInputDevice.__init__(self,
                                     get_pin_for_port(self._pma_port),
                                     pull_up=False,
                                     queue_len=queue_len,
                                     sample_wait=0.06,
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

        Stateful.__init__(self)
        Recreatable.__init__(self, {"port_name": port_name,
                                    "queue_len": queue_len,
                                    "partial": partial,
                                    "name": self.name,
                                    "max_distance": lambda: self.max_distance,
                                    "threshold_distance": lambda: self.threshold_distance})

    def close(self):
        """Shut down the device and release all associated resources. This
        method can be called on an already closed device without raising an
        exception.

        This method is primarily intended for interactive use at the command
        line. It disables the device and releases its pin(s) for use by another
        device.

        You can attempt to do this simply by deleting an object, but unless
        you've cleaned up all references to the object this may not work (even
        if you've cleaned up all references, there's still no guarantee the
        garbage collector will actually delete the object at that point).  By
        contrast, the close method provides a means of ensuring that the object
        is shut down.

        For example, if you have a buzzer connected to port D4, but then wish
        to attach an LED instead:

            >>> from pitop import Buzzer, LED
            >>> bz = Buzzer("D4")
            >>> bz.on()
            >>> bz.off()
            >>> bz.close()
            >>> led = LED("D4")
            >>> led.blink()

        :class:`Device` descendents can also be used as context managers using
        the :keyword:`with` statement. For example:

            >>> from pitop import Buzzer, LED
            >>> with Buzzer("D4") as bz:
            ...     bz.on()
            ...
            >>> with LED("D4") as led:
            ...     led.on()
            ...
        """
        try:
            super(UltrasonicSensorRPI, self).close()
        except RuntimeError:
            PTLogger.debug(f"Ultrasonic Sensor on port {self._pma_port} - "
                           "there was an error in closing the port!")

    @property
    def value(self):
        """Returns a value between 0, indicating that something is either
        touching the sensor or is sufficiently near that the sensor can't tell
        the difference, and 1, indicating that something is at or beyond the
        specified *max_distance*."""
        return super(UltrasonicSensorRPI, self).value

    @property
    def pin(self):
        """Returns the :class:`Pin` that the sensor is connected to.

        This is simply an alias for the usual :attr:`~GPIODevice.pin`
        attribute.
        """
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


UltrasonicSensorRPI.when_out_of_range = UltrasonicSensorRPI.when_activated
UltrasonicSensorRPI.when_in_range = UltrasonicSensorRPI.when_deactivated
UltrasonicSensorRPI.wait_for_out_of_range = UltrasonicSensorRPI.wait_for_active
UltrasonicSensorRPI.wait_for_in_range = UltrasonicSensorRPI.wait_for_inactive
