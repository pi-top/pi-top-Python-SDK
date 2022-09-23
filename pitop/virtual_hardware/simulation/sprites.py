import pygame

import pitop.virtual_hardware.simulation.images as Images


def remove_alpha(image):
    # draw a white background behind image and convert it, losing transparency
    # this improves performance and ensures that snapshots are consistent
    new = image.copy()
    new.fill((255, 255, 255))
    new.blit(image, (0, 0))
    return new.convert()


class Pitop(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = remove_alpha(pygame.image.load(Images.Pitop))
        self.rect = self.image.get_rect()


class LED(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.color = config.get("color", "red")
        self.image = remove_alpha(pygame.image.load(getattr(Images, f"LED_{self.color}_off")))
        self.rect = self.image.get_rect()

    def update(self):
        if self.state and self.state.get("value", False):
            self.image = remove_alpha(pygame.image.load(getattr(Images, f"LED_{self.color}_on")))
        else:
            self.image = remove_alpha(pygame.image.load(getattr(Images, f"LED_{self.color}_off")))


class Button(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = remove_alpha(pygame.image.load(Images.Button))
        self.rect = self.image.get_rect()

    def update(self):
        if self.state and self.state.get("is_pressed", False):
            self.image = remove_alpha(pygame.image.load(Images.Button_pressed))
        else:
            self.image = remove_alpha(pygame.image.load(Images.Button))
