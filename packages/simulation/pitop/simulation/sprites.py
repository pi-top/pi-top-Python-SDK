import pygame

from . import images as Images
from .simsprite import ComponentableSimSprite, SimSprite
from .virtual_hardware import is_virtual_hardware


def remove_alpha(image):
    # draw a white background behind image and convert it, losing transparency
    # this improves performance and ensures that snapshots are consistent
    new = image.copy()
    new.fill((255, 255, 255))
    new.blit(image, (0, 0))
    return new.convert()


class Pitop(pygame.sprite.Sprite, ComponentableSimSprite):
    def __init__(self, config):
        pygame.sprite.Sprite.__init__(self)

        self.image = remove_alpha(pygame.image.load(Images.Pitop))
        self.rect = self.image.get_rect()


class LED(pygame.sprite.Sprite, SimSprite):
    def __init__(self, config):
        pygame.sprite.Sprite.__init__(self)

        self.color = config.get("color", "red")
        self.image = remove_alpha(
            pygame.image.load(getattr(Images, f"LED_{self.color}_off"))
        )
        self.rect = self.image.get_rect()

    def update(self):
        if not hasattr(self, "state"):
            return

        if self.state.get("value", False):
            self.image = remove_alpha(
                pygame.image.load(getattr(Images, f"LED_{self.color}_on"))
            )
        else:
            self.image = remove_alpha(
                pygame.image.load(getattr(Images, f"LED_{self.color}_off"))
            )


class Button(pygame.sprite.Sprite, SimSprite):
    def __init__(self, config):
        pygame.sprite.Sprite.__init__(self)

        self.image = remove_alpha(pygame.image.load(Images.Button))
        self.rect = self.image.get_rect()

    def update(self):
        if not hasattr(self, "state"):
            return

        if self.state.get("is_pressed", False):
            self.image = remove_alpha(pygame.image.load(Images.Button_pressed))
        else:
            self.image = remove_alpha(pygame.image.load(Images.Button))

    @staticmethod
    def handle_event(type, target_name, component):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        if type == pygame.MOUSEBUTTONDOWN and target_name == "main":
            component.pin.drive_low()

        elif type == pygame.MOUSEBUTTONUP:
            component.pin.drive_high()
