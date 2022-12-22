import pygame

from .color import PitopColorScheme
from .utils import multiply_scalar

MARGIN = 10
FONT_SIZE = 22
X_OFFSET = 20


class PortLabel:
    height = 20
    width = 30

    def __init__(self, port_name, Size, scale, pos=None) -> None:
        self.port_name = port_name
        self.scale = scale

        if pos is None:
            pos = (X_OFFSET, self.height)

        font = pygame.font.SysFont(None, int(FONT_SIZE * self.scale))
        label = font.render(self.port_name, True, pygame.Color(self.color))
        label_pos = (pos[0], (pos[1] - label.get_height() / self.scale))

        self.base_image = pygame.Surface(multiply_scalar(self.scale, Size))
        self.base_image.fill(pygame.Color("WHITE"))
        self.base_image.blit(
            label,
            multiply_scalar(self.scale, label_pos),
        )
        pygame.draw.line(
            self.base_image,
            pygame.Color(self.color),
            multiply_scalar(scale, (pos[0], pos[1])),
            multiply_scalar(scale, (pos[0] + self.width, pos[1])),
        )

    @property
    def size(self):
        return multiply_scalar(self.scale, (self.width, self.height))

    @property
    def color(self):
        if isinstance(self.port_name, str) and self.port_name[0] == "A":
            return PitopColorScheme.BLUE
        if isinstance(self.port_name, str) and self.port_name[0] == "D":
            return PitopColorScheme.MAGENTA
        return PitopColorScheme.CHARCOAL

    def render(self, image, pos=None):
        if pos is None:
            pos = (0, self.height + MARGIN)
        base_image = self.base_image.copy()
        base_image.blit(image, multiply_scalar(self.scale, pos))
        return base_image
