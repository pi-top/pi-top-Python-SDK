from math import cos, sin, radians, sqrt

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

    def _generate_sprite_centres(self):
        # sprites for the digital and analog ports are positioned on a circle
        # around the pi-top, with 30 degrees between them

        canvas_centre = (
            int(self._sim_size[0] / 2),
            int(self._sim_size[1] / 2),
        )

        def pythag_hypot(a, b):
            return sqrt(a**2 + b**2)

        def point_on_circle(angle):
            center = canvas_centre
            angle = radians(angle)

            corner_padding = self._sprite.rect.width / 4
            center_to_corner = pythag_hypot(
                self._sprite.rect.width / 2, self._sprite.rect.height / 2)
            radius = center_to_corner + corner_padding

            x = center[0] + (radius * cos(angle))
            y = center[1] + (radius * sin(angle))

            return x,y

        # clockwise from top right
        self.__sprite_centres = {
            "A1": point_on_circle(-75),
            "A0": point_on_circle(-45),
            "D3": point_on_circle(-15),
            "D2": point_on_circle(15),
            "D1": point_on_circle(45),
            "D0": point_on_circle(75),
            "A3": point_on_circle(180-75),
            "A2": point_on_circle(180-45),
            "D7": point_on_circle(180 -15),
            "D6": point_on_circle(180+15),
            "D5": point_on_circle(180+45),
            "D4": point_on_circle(180+75),
        }
