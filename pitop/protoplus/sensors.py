from gpiozero import DistanceSensor as gpiozero_DistanceSensor


class DistanceSensor(gpiozero_DistanceSensor):
    """Encapsulates the behaviour of a simple DistanceSensor that can be turned
    on and off.

    :param str trigger_gpio_pin: GPIO pin for trigger input
    :param str echo_gpio_pin: GPIO pin for echo response
    """

    def __init__(self, trigger_gpio_pin=23, echo_gpio_pin=27):
        gpiozero_DistanceSensor.__init__(self, echo_gpio_pin, trigger_gpio_pin)

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
        super(DistanceSensor, self).close()

    ##################
    # Legacy methods #
    ##################
    @property
    def raw_distance(self):
        return self.distance

    def get_raw_distance(self):
        return self.distance

    def get_distance(self):
        return self.distance
