from gpiozero import LED as gpiozero_LED
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma.common import get_pin_for_port


class LED(Stateful, Recreatable, gpiozero_LED):
    """Encapsulates the behaviour of an LED.

    An LED (Light Emitting Diode) is a simple light source that can be controlled directly.

    :param str port_name: The ID for the port to which this component is connected
    """

    def __init__(self, port_name, name="led"):
        self._pma_port = port_name
        self.name = name

        Stateful.__init__(self)
        Recreatable.__init__(self, {"port_name": port_name, "name": self.name})
        gpiozero_LED.__init__(self, get_pin_for_port(self._pma_port))

    @property
    def own_state(self):
        return {
            "is_lit": self.is_lit,
            "value": self.value,
        }

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
        super(gpiozero_LED, self).close()
