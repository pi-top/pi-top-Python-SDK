from gpiozero import LED as gpiozero_LED
from PIL import Image

import pitop.common.images as Images
from pitop.core.mixins import Recreatable, Simulatable, Stateful
from pitop.pma.common import get_pin_for_port


class LED(Stateful, Recreatable, Simulatable, gpiozero_LED):
    """Encapsulates the behaviour of an LED.

    An LED (Light Emitting Diode) is a simple light source that can be controlled directly.

    :param str port_name: The ID for the port to which this component is connected
    """

    def __init__(self, port_name, name="led"):
        self._pma_port = port_name
        self.name = name
        self._sprite_id = None

        Stateful.__init__(self)
        Recreatable.__init__(self, {"port_name": port_name, "name": self.name})
        Simulatable.__init__(self, size=(55, 55))
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
        super(LED, self).close()

    def _create_sprites(self, canvas, pos):
        self._sprite_id = canvas.create_image(
            pos[0] + int(self._sim_size[0] / 2),
            pos[1] + int(self._sim_size[1] / 2),
        )

    def _update_sprites(self, canvas):
        image_path = Images.LED_green_on
        if not self.state.get("value", False):
            image_path = Images.LED_green_off

        self._set_sprite_image(
            canvas, sprite_id=self._sprite_id, image=Image.open(image_path)
        )
