from gpiozero import Button
from .common import get_pin_for_port


class PMAButton(Button):
    """
    Encapsulates the behaviour of a push-button.

    A push-button is a simple switch mechanism for controlling some aspect of a circuit.

    :param str port_name: The ID for the port to which this component is connected
    """

    def __init__(self, port_name):
        super(PMAButton, self).__init__(get_pin_for_port(port_name))

    def close(self):
        """
        Shut down the device and release all associated resources. This method
        can be called on an already closed device without raising an exception.

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

            >>> from ptpma import PMABuzzer
            >>> from ptpma import PMALed
            >>> bz = PMABuzzer("D4")
            >>> bz.on()
            >>> bz.off()
            >>> bz.close()
            >>> led = PMALed("D4")
            >>> led.blink()

        :class:`Device` descendents can also be used as context managers using
        the :keyword:`with` statement. For example:

            >>> from ptpma import PMABuzzer
            >>> from ptpma import PMALed
            >>> with PMABuzzer("D4") as bz:
            ...     bz.on()
            ...
            >>> with PMALed("D4") as led:
            ...     led.on()
            ...
        """
        super(PMAButton, self).close()
