from math import cos, sin, radians, sqrt

import pygame

from . import sprites as Sprites


# this is based on the inital further-link graphics area dimensions of 720x680
# multiplied by 2 to leave plenty space around our pi-top image of 435x573
PITOP_SIM_SIZE = (1560, 1240)
PMA_CUBE_SIM_SIZE = (122, 122)


class SimSprite:
    Size = PMA_CUBE_SIM_SIZE

    @classmethod
    def create_sprite_group(cls, sim_size, config):
        sprite_group = pygame.sprite.Group()

        # create the main sprite
        sprite = cls(config)
        sprite.name = "main"

        # position main sprite in center
        center = int(sim_size[0] / 2), int(sim_size[1]/ 2)
        sprite.rect.x = center[0] - int(sprite.rect.width / 2)
        sprite.rect.y = center[1] - int(sprite.rect.height / 2)

        sprite_group.add(sprite)
        return sprite_group

    @staticmethod
    def handle_event(type, target_name, component):
        pass


class ComponentableSimSprite(SimSprite):
    Size = PITOP_SIM_SIZE

    @classmethod
    def create_sprite_group(cls, sim_size, config):
        sprite_group = super().create_sprite_group(sim_size, config)

        main_sprite_rect = sprite_group.sprites()[0].rect
        sprite_centres = cls._generate_sprite_centres(sim_size, main_sprite_rect)

        components = config.get('components', {})
        for component in components.values():
            sprite_class = getattr(Sprites, component.get('classname'))
            sprite = sprite_class(component)
            if not sprite:
                continue

            sprite_centre = sprite_centres.get(
                component.get("port_name", None), (0, 0)
            )

            sprite.rect.x = sprite_centre[0] - int(sprite.rect.width / 2)
            sprite.rect.y = sprite_centre[1] - int(sprite.rect.height / 2)

            sprite.name = component.get("name")
            sprite_group.add(sprite)

        return sprite_group

    @staticmethod
    def handle_event(type, target_name, component):
        for _, child in component.children_gen():
            t_name = "main" if child.config.get('name') == target_name else None
            sprite_class = getattr(Sprites, child.config.get('classname'))
            sprite_class.handle_event(type, t_name, child)

    @staticmethod
    def _generate_sprite_centres(sim_size, main_sprite_rect):
        # sprites for the digital and analog ports are positioned on a circle
        # around the pi-top, with 30 degrees between them

        canvas_centre = int(sim_size[0] / 2), int(sim_size[1] / 2)

        def pythag_hypot(a, b):
            return sqrt(a**2 + b**2)

        def point_on_circle(angle):
            center = canvas_centre
            angle = radians(angle)

            corner_padding = main_sprite_rect.width / 4
            center_to_corner = pythag_hypot(
                main_sprite_rect.width / 2, main_sprite_rect.height / 2)
            radius = center_to_corner + corner_padding

            x = center[0] + (radius * cos(angle))
            y = center[1] + (radius * sin(angle))

            return x,y

        # clockwise from top right
        return {
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
