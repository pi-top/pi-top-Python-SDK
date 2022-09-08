import pygame

import pitop.common.images as Images
from pitop.common.singleton import Singleton
from pitop.core.mixins import (
    Componentable,
    Simulatable,
    SupportsBattery,
    SupportsMiniscreen,
)
from pitop.core.mixins.simulatable import DEFAULT_SIZE


class Pitop(
    SupportsMiniscreen, SupportsBattery, Componentable, Simulatable, metaclass=Singleton
):
    """Represents a pi-top Device.

    When creating a `Pitop` object, multiple properties will be set,
    depending on the pi-top device that it's running the code. For example, if run on
    a pi-top [4], a `miniscreen` attribute will be created as an interface to control the
    miniscreen OLED display, but that won't be available for other pi-top devices.

    The Pitop class is a Singleton. This means that only one instance per process will
    be created. In practice, this means that if in a particular project you instance a Pitop
    class in 2 different files, they will share the internal state.

    *property* miniscreen
        If using a pi-top [4], this property returns a :class:`pitop.miniscreen.Miniscreen` object, to interact with the device's Miniscreen.


    *property* oled
        Refer to `miniscreen`.


    *property* battery
        If using a pi-top with a battery, this property returns a :class:`pitop.battery.Battery` object, to interact with the device's battery.
    """

    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        Componentable.__init__(self)
        Simulatable.__init__(self, size=DEFAULT_SIZE)

        canvas_centre = (
            int(self._sim_size[0] / 2),
            int(self._sim_size[1] / 2),
        )

        self.__sprite_centres = {
            "D0": (canvas_centre[0] + 200, canvas_centre[1] - 200),
            "D1": (canvas_centre[0] + 230, canvas_centre[1] - 100),
            "D2": (canvas_centre[0] + 240, canvas_centre[1]),
            "D3": (canvas_centre[0] + 230, canvas_centre[1] + 100),
            "D4": (canvas_centre[0] + 200, canvas_centre[1] + 200),
        }

    def _create_sprite(self):
        sprite_group = pygame.sprite.Group()

        pitop_sprite = PitopSprite()
        sprite_group.add(pitop_sprite)

        center = int(self._sim_size[0] / 2), int(self._sim_size[1]/ 2)
        pitop_sprite.rect.x = center[0] - int(pitop_sprite.rect.width / 2)
        pitop_sprite.rect.y = center[1] - int(pitop_sprite.rect.height / 2)


        # create child sprites
        for child_name in self.children:
            child = getattr(self, child_name, None)

            if isinstance(child, Simulatable):

                sprite_centre = self.__sprite_centres.get(
                    child.config.get("port_name", None), (0, 0)
                )

                child_sprite = child._create_sprite()
                child_sprite.rect.x = sprite_centre[0] - int(child_sprite.rect.width / 2)
                child_sprite.rect.y = sprite_centre[1] - int(child_sprite.rect.height / 2)

                sprite_group.add(child_sprite)

        return sprite_group

    def _handle_event(self, event):
        for child_name in self.children:
            child = getattr(self, child_name, None)
            if isinstance(child, Simulatable):
                child._handle_event(event)


class PitopSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load(Images.Pitop)
        self.rect = self.image.get_rect()
