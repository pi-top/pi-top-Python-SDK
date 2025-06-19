import math

from .widget import WidgetBase


class Slider(WidgetBase):
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(x, y, width, height)

        import pygame

        self.pygame = pygame

        self.selected = False

        self.min = kwargs.get("min", 0)
        self.max = kwargs.get("max", 99)
        self.step = kwargs.get("step", 1)

        self.colour = kwargs.get("colour", (200, 200, 200))
        self.handleColour = kwargs.get("handleColour", (0, 0, 0))

        self.borderThickness = kwargs.get("borderThickness", 3)
        self.borderColour = kwargs.get("borderColour", (0, 0, 0))

        self.value = self.round(kwargs.get("initial", (self.max + self.min) / 2))
        self.value = max(min(self.value, self.max), self.min)

        self.curved = kwargs.get("curved", True)

        self.vertical = kwargs.get("vertical", False)

        self.parent_x = kwargs.get("parent_x", 0)
        self.parent_y = kwargs.get("parent_y", 0)

        if self.curved:
            if self.vertical:
                self.radius = self.width // 2
            else:
                self.radius = self.height // 2

        if self.vertical:
            self.handleRadius = kwargs.get("handleRadius", int(self.width / 1.3))
        else:
            self.handleRadius = kwargs.get("handleRadius", int(self.height / 1.3))

    @property
    def pos(self):
        return (self.x, self.y)

    def update(self):

        x, y = self.pygame.mouse.get_pos()
        x = x - self.parent_x
        y = y - self.parent_y

        if self.selected:
            if self.vertical:
                self.value = self.max - self.round(
                    (y - self.y) / self.height * self.max
                )
                self.value = max(min(self.value, self.max), self.min)
            else:
                self.value = self.round((x - self.x) / self.width * self.max + self.min)
                self.value = max(min(self.value, self.max), self.min)

    def handle_event(self, event):
        if not self._hidden and not self._disabled:
            if event.type == self.pygame.MOUSEBUTTONDOWN and self.contains(
                *self.pygame.mouse.get_pos()
            ):
                self.selected = True
            elif event.type == self.pygame.MOUSEBUTTONUP:
                self.selected = False

    def draw(self, surface):
        if not self._hidden:
            self.pygame.draw.rect(
                surface, self.colour, (self.x, self.y, self.width, self.height)
            )

            if self.vertical:
                if self.curved:
                    self.pygame.draw.circle(
                        surface,
                        self.colour,
                        (self.x + self.width // 2, self.y),
                        self.radius,
                    )
                    self.pygame.draw.circle(
                        surface,
                        self.colour,
                        (self.x + self.width // 2, self.y + self.height),
                        self.radius,
                    )
                circle = (
                    self.x + self.width // 2,
                    int(
                        self.y
                        + (self.max - self.value) / (self.max - self.min) * self.height
                    ),
                )
            else:
                if self.curved:
                    self.pygame.draw.circle(
                        surface,
                        self.colour,
                        (self.x, self.y + self.height // 2),
                        self.radius,
                    )
                    self.pygame.draw.circle(
                        surface,
                        self.colour,
                        (self.x + self.width, self.y + self.height // 2),
                        self.radius,
                    )
                circle = (
                    int(
                        self.x
                        + (self.value - self.min) / (self.max - self.min) * self.width
                    ),
                    self.y + self.height // 2,
                )

            from pygame import gfxdraw

            gfxdraw.filled_circle(
                surface, *circle, self.handleRadius, self.handleColour
            )
            gfxdraw.aacircle(surface, *circle, self.handleRadius, self.handleColour)

    def contains(self, x, y):
        x = x - self.parent_x
        y = y - self.parent_y

        if self.vertical:
            handleX = self.x + self.width // 2
            handleY = int(
                self.y + (self.max - self.value) / (self.max - self.min) * self.height
            )
        else:
            handleX = int(
                self.x + (self.value - self.min) / (self.max - self.min) * self.width
            )
            handleY = self.y + self.height // 2

        if math.sqrt((handleX - x) ** 2 + (handleY - y) ** 2) <= self.handleRadius:
            return True

        return False

    def round(self, value):
        return self.step * round(value / self.step)
