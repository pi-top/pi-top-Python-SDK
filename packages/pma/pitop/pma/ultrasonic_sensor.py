from pitop.core.mixins import Recreatable, Stateful
from pitop.pma.common.utils import Port

from .ultrasonic_sensor_base import UltrasonicSensorMCU, UltrasonicSensorRPI

valid_analog_ports = ["A1", "A3"]


class UltrasonicSensor(Stateful, Recreatable):
    def __init__(
        self,
        port_name,
        queue_len=5,
        max_distance=3,
        threshold_distance=0.3,
        partial=False,
        name="ultrasonic",
    ):
        assert port_name in Port
        self._pma_port = port_name
        self.name = name

        if port_name in valid_analog_ports:
            self.__ultrasonic_device = UltrasonicSensorMCU(
                port_name=port_name,
                queue_len=queue_len,
                max_distance=max_distance,
                threshold_distance=threshold_distance,
                partial=partial,
                name=name,
            )
        else:
            self.__ultrasonic_device = UltrasonicSensorRPI(
                port_name=port_name,
                queue_len=queue_len,
                max_distance=max_distance,
                threshold_distance=threshold_distance,
                partial=partial,
                name=name,
            )

        self._in_range_function = None
        self._out_of_range_function = None

        Stateful.__init__(self)
        Recreatable.__init__(
            self,
            {
                "port_name": port_name,
                "queue_len": queue_len,
                "partial": partial,
                "name": self.name,
                "max_distance": lambda: self.max_distance,
                "threshold_distance": lambda: self.threshold_distance,
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def own_state(self):
        return {
            "distance": self.distance,
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
        return self.__ultrasonic_device.max_distance

    @max_distance.setter
    def max_distance(self, value):
        self.__ultrasonic_device.max_distance = value

    @property
    def threshold_distance(self):
        """The distance, measured in meters, that will trigger the
        :attr:`when_in_range` and :attr:`when_out_of_range` events when
        crossed.

        This is simply a meter-scaled variant of the usual
        :attr:`~SmoothedInputDevice.threshold` attribute.
        """
        return self.__ultrasonic_device.threshold_distance

    @threshold_distance.setter
    def threshold_distance(self, value):
        self.__ultrasonic_device.threshold_distance = value

    @property
    def distance(self):
        """Returns the current distance measured by the sensor in meters.

        Note
        that this property will have a value between 0 and
        :attr:`max_distance`.
        """
        return self.__ultrasonic_device.distance

    @property
    def value(self):
        """Returns a value between 0, indicating that something is either
        touching the sensor or is sufficiently near that the sensor can't tell
        the difference, and 1, indicating that something is at or beyond the
        specified *max_distance*."""
        return self.__ultrasonic_device.value

    @property
    def pin(self):
        return self.__ultrasonic_device.pin

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

        For example, if you have a buzzer connected to port D0, but then wish
        to attach an LED instead:

            >>> from pitop import Buzzer, LED
            >>> bz = Buzzer("D0")
            >>> bz.on()
            >>> bz.off()
            >>> bz.close()
            >>> led = LED("D0")
            >>> led.blink()

        :class:`Device` descendents can also be used as context managers using
        the :keyword:`with` statement. For example:

            >>> from pitop import Buzzer, LED
            >>> with Buzzer("D0") as bz:
            ...     bz.on()
            ...
            >>> with LED("D0") as led:
            ...     led.on()
            ...
        """
        self.__ultrasonic_device.close()

    @property
    def in_range(self):
        return self.__ultrasonic_device.in_range

    @property
    def when_in_range(self):
        return self.__ultrasonic_device.when_deactivated

    @when_in_range.setter
    def when_in_range(self, function):
        if callable(function):
            self.__ultrasonic_device.when_deactivated = function

    @property
    def when_out_of_range(self):
        return self.__ultrasonic_device.when_activated

    @when_out_of_range.setter
    def when_out_of_range(self, function):
        if callable(function):
            self.__ultrasonic_device.when_activated = function

    def wait_for_in_range(self, timeout=None):
        self.__ultrasonic_device.wait_for_inactive(timeout=timeout)

    def wait_for_out_of_range(self, timeout=None):
        self.__ultrasonic_device.wait_for_active(timeout=timeout)
