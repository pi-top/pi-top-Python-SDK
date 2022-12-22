from dataclasses import dataclass
from typing import Any, Tuple

import pygame

from . import images as Images
from .color import PitopColorScheme
from .events import SimEvent, SimEventTypes
from .images import PMA_CUBE_SIZE
from .port_label import PortLabel
from .simsprite import ComponentableSimSprite, SimSprite
from .utils import multiply_scalar
from .virtual_hardware import is_virtual_hardware
from .widgets.slider import Slider

MARGIN = 10
SLIDER_WIDTH = 85
SLIDER_HEIGHT = 8
SLIDER_HANDLE_RADIUS = 8
FONT_SIZE = 22
TEXT_OFFSET = (-13, 8)


class Pitop(pygame.sprite.Sprite, ComponentableSimSprite):
    def __init__(self, config, scale):
        pygame.sprite.Sprite.__init__(self)

        self.scale = scale
        self.miniscreen_pos = multiply_scalar(scale, Images.Pitop_miniscreen_pos)

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
            size = multiply_scalar(self.scale, rgb.size)
            image = pygame.transform.scale(miniscreen_surface, size)
            self.image.blit(image, self.miniscreen_pos)


class LED(pygame.sprite.Sprite, SimSprite):
    def __init__(self, config, scale, draw_port=False):
        pygame.sprite.Sprite.__init__(self)

        self.color = config.get("color", "red")
        self.off_image = SimSprite._load_image(
            getattr(Images, f"LED_{self.color}_off"), scale
        )
        self.on_image = SimSprite._load_image(
            getattr(Images, f"LED_{self.color}_on"), scale
        )

        if draw_port:
            self.Size = (self.Size[0], self.Size[1] + PortLabel.height + MARGIN)
            port_label = PortLabel(
                config.get("port_name"),
                self.Size,
                scale,
                pos=(int(self.Size[0]) / 2 - 40, PortLabel.height),
            )
            self.on_image = port_label.render(self.on_image)
            self.off_image = port_label.render(self.off_image)

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
    def __init__(self, config, scale, draw_port=False):
        pygame.sprite.Sprite.__init__(self)

        self.released_image = SimSprite._load_image(Images.Button, scale)
        self.pressed_image = SimSprite._load_image(Images.Button_pressed, scale)

        if draw_port:
            self.Size = (self.Size[0], self.Size[1] + PortLabel.height + MARGIN)
            port_label = PortLabel(
                config.get("port_name"),
                self.Size,
                scale,
                pos=(int(self.Size[0]) / 2 - 40, PortLabel.height),
            )
            self.released_image = port_label.render(self.released_image)
            self.pressed_image = port_label.render(self.pressed_image)

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
    def handle_sim_event(e: SimEvent, component):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        if e.type == SimEventTypes.MOUSE_DOWN:
            component.pin.drive_low()

        elif e.type == SimEventTypes.MOUSE_UP:
            component.pin.drive_high()


class Buzzer(pygame.sprite.Sprite, SimSprite):
    Size = ((PMA_CUBE_SIZE[0]) * 2, PMA_CUBE_SIZE[0])

    def __init__(self, config, scale, draw_port=False):
        pygame.sprite.Sprite.__init__(self)

        def get_pos(image):
            return (
                int((self.Size[0] * scale - image.get_width()) / 2),
                int((self.Size[1] * scale - image.get_height()) / 2),
            )

        self.component_image = SimSprite._load_image(Images.Buzzer, scale)
        self.component_pos = get_pos(self.component_image)

        self.buzzer_sound_image = SimSprite._load_image(Images.buzzer_sound_icon, scale)
        self.buzzer_sound_image_pos = get_pos(self.buzzer_sound_image)

        self.base_image = pygame.Surface(multiply_scalar(scale, self.Size))
        self.base_image.fill(pygame.Color("WHITE"))

        if draw_port:
            label_height = PortLabel.height + MARGIN
            self.Size = (self.Size[0], self.Size[1] + label_height)
            port_label = PortLabel(
                config.get("port_name"),
                self.Size,
                scale,
                pos=(int(self.Size[0]) / 2 - 30, PortLabel.height),
            )
            self.base_image = port_label.render(self.base_image)
            self.component_pos = (
                self.component_pos[0],
                self.component_pos[1] + scale * label_height,
            )
            self.buzzer_sound_image_pos = (
                self.buzzer_sound_image_pos[0],
                self.buzzer_sound_image_pos[1] + scale * label_height,
            )

        self.rect = self.base_image.get_rect()

    def render(self):
        value = False
        if hasattr(self, "state"):
            value = self.state.get("value", False)

        image = self.base_image.copy()
        if value:
            image.blit(self.buzzer_sound_image, self.buzzer_sound_image_pos)

        image.blit(self.component_image, self.component_pos)

        return image

    def update(self):
        if not hasattr(self, "state"):
            return

        self.image = self.render()


@dataclass
class Component:
    pos: Tuple
    obj: Any


class SliderSensorSprite(pygame.sprite.Sprite, SimSprite):
    slider: Slider
    font: Component
    icon: Component
    img: Component
    scale: float

    image: str
    icon: str
    measurement_key_in_state: str
    min_value: int = 0
    max_value: int = 999
    slider_step: int = 1

    def __init__(self, config, scale, draw_port=False):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale

        self.port_label = None
        if draw_port:
            self.Size = (self.Size[0], self.Size[1] + PortLabel.height + MARGIN)
            self.port_label = PortLabel(config.get("port_name"), self.Size, scale)

        self.create_components()
        assert self.slider is not None
        assert self.font is not None
        assert self.icon is not None
        assert self.img is not None

        self.base_image = self.draw_base_image()

        if not is_virtual_hardware():
            self.slider.disable()

        self.image = self.render()
        self.rect = self.image.get_rect()

    def create_components(self):
        label_height = (
            self.scale * (PortLabel.height + MARGIN) if self.port_label else 0
        )
        right_hand_side_x_start = self.Size[0] - SLIDER_WIDTH - SLIDER_HANDLE_RADIUS - 1

        slider_pos = (
            right_hand_side_x_start,
            self.Size[1] - MARGIN - SLIDER_HEIGHT,
        )
        slider_pos = multiply_scalar(self.scale, slider_pos)

        self.slider = Slider(
            x=slider_pos[0],
            y=slider_pos[1],
            width=int(SLIDER_WIDTH * self.scale),
            height=int(SLIDER_HEIGHT * self.scale),
            min=self.min_value,
            max=self.max_value,
            step=self.slider_step,
            initial=0,
            handleRadius=int(SLIDER_HANDLE_RADIUS * self.scale),
            handleColour=pygame.Color(PitopColorScheme.CHARCOAL),
            colour=pygame.Color(PitopColorScheme.GRAY),
        )

        text_pos = (
            slider_pos[0] + self.slider.width / 2 + TEXT_OFFSET[0] * self.scale,
            slider_pos[1] - MARGIN * 2 * self.scale,
        )

        self.font = Component(
            text_pos, pygame.font.SysFont(None, int(FONT_SIZE * self.scale))
        )

        icon_image = SimSprite._load_image(self.icon, self.scale)
        icon_pos = (
            slider_pos[0] + self.slider.width / 2 - icon_image.get_width() / 2,
            text_pos[1]
            - icon_image.get_height()
            - self.scale * MARGIN / 2
            - label_height,
        )
        self.icon = Component(icon_pos, icon_image)

        self.img = Component(
            (0, 0),
            SimSprite._load_image(self.image, self.scale),
        )

    def draw_base_image(self):
        base_image = pygame.Surface(multiply_scalar(self.scale, self.Size))
        base_image.fill(pygame.Color("WHITE"))
        base_image.blit(self.img.obj, self.img.pos)
        base_image.blit(self.icon.obj, self.icon.pos)

        if self.port_label:
            base_image = self.port_label.render(base_image)

        return base_image

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.slider.parent_x = x
        self.slider.parent_y = y

    def render(self):
        value = 0
        if hasattr(self, "state"):
            value = self.state.get(self.measurement_key_in_state, 0)

        image = self.base_image.copy()
        image.blit(
            self.font.obj.render(
                str(value), True, pygame.Color(PitopColorScheme.CHARCOAL)
            ),
            self.font.pos,
        )

        if not self.slider.selected:
            self.slider.value = value

        self.slider.draw(image)

        return image

    def update(self):
        if not hasattr(self, "state"):
            return

        self.slider.update()
        self.image = self.render()

    @staticmethod
    def handle_sim_event(e: SimEvent, component):
        if not is_virtual_hardware():
            return

        if e.value is None:
            e.value = 0

        if e.type == SimEventTypes.SLIDER_UPDATE:
            component.read.return_value = e.value

    def handle_pygame_event(self, e: pygame.event.Event):
        self.slider.handle_event(e)


class LightSensor(SliderSensorSprite):
    Size = (PMA_CUBE_SIZE[0] * 2 + MARGIN, PMA_CUBE_SIZE[1])
    image = Images.LightSensor
    measurement_key_in_state = "reading"
    icon = Images.lightbulb_icon


class SoundSensor(SliderSensorSprite):
    Size = (PMA_CUBE_SIZE[0] * 2 + MARGIN, PMA_CUBE_SIZE[1])
    image = Images.SoundSensor
    max_value = 500
    measurement_key_in_state = "reading"
    icon = Images.speaker_icon

    @staticmethod
    def handle_sim_event(e: SimEvent, component):
        if not is_virtual_hardware():
            return

        if e.value is None:
            e.value = 0

        if e.type == SimEventTypes.SLIDER_UPDATE:
            # since 'reading' is a property of SoundSensor, it's treated differently
            # see 'mock_pitop()' in pitop.py
            reading_mock = component._mock.get("reading")
            reading_mock.return_value = e.value


class Potentiometer(SliderSensorSprite):
    Size = (PMA_CUBE_SIZE[0] * 2 + MARGIN, PMA_CUBE_SIZE[1])
    image = Images.Potentiometer
    measurement_key_in_state = "position"
    icon = Images.angle_icon


class UltrasonicSensor(SliderSensorSprite):
    Size = (PMA_CUBE_SIZE[0] * 3 + MARGIN, PMA_CUBE_SIZE[1])
    image = Images.UltrasonicSensor
    max_value = 3
    measurement_key_in_state = "distance"
    icon = Images.distance_icon
    slider_step = 0.1

    @staticmethod
    def handle_sim_event(e: SimEvent, component):
        if not is_virtual_hardware():
            return

        if e.value is None:
            e.value = 0
        if e.type == SimEventTypes.SLIDER_UPDATE and hasattr(component, "_mock"):
            # since 'distance' is a property of UltrasonicSensor, it's treated differently
            # see 'mock_pitop()' in pitop.py
            distance_mock = component._mock.get("distance")
            distance_mock.return_value = float("{:.2f}".format(e.value))
