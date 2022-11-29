import pygame

from . import images as Images
from .simsprite import ComponentableSimSprite, SimSprite
from .virtual_hardware import is_virtual_hardware


class Pitop(pygame.sprite.Sprite, ComponentableSimSprite):
    def __init__(self, config, scale):
        pygame.sprite.Sprite.__init__(self)

        self.scale = scale
        self.miniscreen_pos = [scale * x for x in Images.Pitop_miniscreen_pos]

        self.image = SimSprite._load_image(Images.Pitop, scale)
        self.rect = self.image.get_rect()

    def update(self):
        if not hasattr(self, "state"):
            return

        miniscreen_image = self.state.get("miniscreen_image", False)
        if miniscreen_image:
            rgb = miniscreen_image.convert("RGB")
            miniscreen_surface = pygame.image.fromstring(
                rgb.tobytes(), rgb.size, rgb.mode
            )
            size = [self.scale * x for x in rgb.size]
            image = pygame.transform.scale(miniscreen_surface, size)
            self.image.blit(image, self.miniscreen_pos)


class LED(pygame.sprite.Sprite, SimSprite):
    def __init__(self, config, scale):
        pygame.sprite.Sprite.__init__(self)

        self.color = config.get("color", "red")
        self.off_image = SimSprite._load_image(
            getattr(Images, f"LED_{self.color}_off"), scale
        )
        self.on_image = SimSprite._load_image(
            getattr(Images, f"LED_{self.color}_on"), scale
        )

        self.image = self.off_image
        self.rect = self.image.get_rect()

    def update(self):
        if not hasattr(self, "state"):
            return

        if self.state.get("value", False):
            self.image = self.on_image
        else:
            self.image = self.off_image


class Button(pygame.sprite.Sprite, SimSprite):
    def __init__(self, config, scale):
        pygame.sprite.Sprite.__init__(self)

        self.released_image = SimSprite._load_image(Images.Button, scale)
        self.pressed_image = SimSprite._load_image(Images.Button_pressed, scale)

        self.image = self.released_image
        self.rect = self.image.get_rect()

    def update(self):
        if not hasattr(self, "state"):
            return

        if self.state.get("is_pressed", False):
            self.image = self.pressed_image
        else:
            self.image = self.released_image

    @staticmethod
    def handle_event(type, target_name, component):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        if type == pygame.MOUSEBUTTONDOWN and target_name == "main":
            component.pin.drive_low()

        elif type == pygame.MOUSEBUTTONUP:
            component.pin.drive_high()
