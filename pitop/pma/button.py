from tkinter import Button as TkInterButton

from gpiozero import Button as gpiozero_Button
from PIL import Image

import pitop.common.images as Images
from pitop.core.mixins import Recreatable, Simulatable, Stateful
from pitop.pma.common import get_pin_for_port


class Button(Stateful, Recreatable, Simulatable, gpiozero_Button):
    """Encapsulates the behaviour of a push-button.

    A push-button is a simple switch mechanism for controlling some aspect of a circuit.

    :param str port_name: The ID for the port to which this component is connected
    """

    def __init__(self, port_name, name="button"):
        self._pma_port = port_name
        self.name = name
        self._sprite = None

        Stateful.__init__(self)
        Recreatable.__init__(self, {"port_name": port_name, "name": self.name})
        Simulatable.__init__(self, size=(55, 55))
        gpiozero_Button.__init__(self, get_pin_for_port(self._pma_port))

    @property
    def own_state(self):
        return {
            "is_held": self.is_held,
            "is_pressed": self.is_pressed,
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
        super(Button, self).close()

    def _create_sprites(self, canvas, pos):
        def set_button_pressed(pressed):
            self._fire_events(self.pin_factory.ticks(), pressed)

        self._sprite = TkInterButton(canvas, borderwidth=0)
        self._set_sprite_image(
            canvas, sprite=self._sprite, image=Image.open(Images.Button)
        )
        self._sprite.place(x=pos[0], y=pos[1])

        self._sprite.bind("<ButtonRelease>", lambda _: set_button_pressed(False))
        self._sprite.bind("<ButtonPress>", lambda _: set_button_pressed(True))
