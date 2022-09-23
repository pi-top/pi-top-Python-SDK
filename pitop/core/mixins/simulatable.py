from time import sleep
from threading import Thread
from multiprocessing import Process, Pipe, Queue, Event
from math import cos, sin, radians, sqrt
import sys

import pygame
from PIL import Image

import pitop.common.images as Images
from pitop.virtual_hardware import is_virtual_hardware


# this is based on the inital further-link graphics area dimensions of 780x620
# multiplied by 2 to leave plenty space around our pi-top image of 435x573
DEFAULT_SIZE = (1560, 1240)

import os
from io import BytesIO
def to_bytes(image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

def _run_sim(size, config, stop_ev, state_q, out_event_q, in_event_q, snapshot_ev, snapshot_q):
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    width, height = size
    screen = pygame.display.set_mode([width, height])
    screen.fill((255, 255, 255))

    sprite_group = _create_sprite_group(size, config)
    if not sprite_group:
        stop_ev.set()

    OUTBOUND_EVENTS = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]

    while not stop_ev.is_set():
        for event in pygame.event.get():
            target = None
            if event.type == pygame.QUIT:
                stop_ev.set()
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in sprite_group.sprites():
                    if not isinstance(sprite, ButtonSprite):
                        continue
                    rect = sprite.rect
                    if (
                        rect.x <= event.pos[0] <= rect.x + rect.width and
                        rect.y <= event.pos[1] <= rect.y + rect.height
                    ):
                        target = sprite.name
            if (event.type in OUTBOUND_EVENTS):
                out_event_q.put((event.type, target))

        while not in_event_q.empty():
            type, target_name = in_event_q.get_nowait()
            target = [s for s in sprite_group.sprites() if s.name == target_name]
            if not len(target):
                continue
            pos = (target[0].rect.x, target[0].rect.y)
            event = pygame.event.Event(type, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
            pygame.event.post(event)

        if snapshot_ev.is_set():
            snapshot = to_bytes(Image.frombytes("RGB", size, bytes(pygame.image.tostring(screen, "RGB"))))
            snapshot_q.put(snapshot)
            snapshot_ev.clear()

        while not state_q.empty():
            state = state_q.get_nowait()
            for sprite in sprite_group.sprites():
                if sprite.name == "main":
                    sprite.state = state
                else:
                    sprite.state = state.get(sprite.name)

        sprite_group.update()
        sprite_group.draw(screen)
        pygame.display.flip()

        clock.tick(20)

    # Don't pygame.quit() - isn't needed and can cause X server to crash
    sys.exit()


def _generate_sprite_centres(sim_size, main_sprite):
    # sprites for the digital and analog ports are positioned on a circle
    # around the pi-top, with 30 degrees between them

    canvas_centre = int(sim_size[0] / 2), int(sim_size[1] / 2)

    def pythag_hypot(a, b):
        return sqrt(a**2 + b**2)

    def point_on_circle(angle):
        center = canvas_centre
        angle = radians(angle)

        corner_padding = main_sprite.rect.width / 4
        center_to_corner = pythag_hypot(
            main_sprite.rect.width / 2, main_sprite.rect.height / 2)
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


def _create_sprite(config):
    sprite_class = f"{config.get('classname')}Sprite"
    try:
        return globals()[sprite_class](config)
    except Exception as e:
        print(f"Error creating sprite for {config.get('classname')}, {e}")
        return None


def _create_sprite_group(sim_size, config):
    sprite_group = pygame.sprite.Group()

    sprite = _create_sprite(config)
    if not sprite:
        return None

    # position main sprite in center
    center = int(sim_size[0] / 2), int(sim_size[1]/ 2)
    sprite.rect.x = center[0] - int(sprite.rect.width / 2)
    sprite.rect.y = center[1] - int(sprite.rect.height / 2)

    sprite.name = "main"
    sprite_group.add(sprite)

    sprite_centres = _generate_sprite_centres(sim_size, sprite)

    components = config.get('components', {})
    for component in components.values():
        sprite = _create_sprite(component)
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

def remove_alpha(image):
    new = image.copy()
    new.fill((255, 255, 255))
    new.blit(image, (0, 0))
    return new.convert()

class PitopSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = remove_alpha(pygame.image.load(Images.Pitop))
        self.rect = self.image.get_rect()


class LEDSprite(pygame.sprite.Sprite):
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


class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = remove_alpha(pygame.image.load(Images.Button))
        self.rect = self.image.get_rect()

    def update(self):
        if self.state and self.state.get("is_pressed", False):
            self.image = remove_alpha(pygame.image.load(Images.Button_pressed))
        else:
            self.image = remove_alpha(pygame.image.load(Images.Button))


class Simulatable:
    """Represents an object that can be simulated on a digital canvas."""

    def __init__(self, size=DEFAULT_SIZE):
        # TODO must be Recreatable and Stateful
        self._sim_size = size

        self._sim_process = None
        self._sim_stop_ev = None
        self._sim_state_q = None
        self._sim_out_event_q = None
        self._sim_in_event_q = None
        self._sim_snapshot_ev = None
        self._sim_snapshot_q = None

    def __del__(self):
        self.stop_simulation()

    def simulate(self):
        self.stop_simulation()

        self._sim_stop_ev = Event()
        self._sim_state_q = Queue()
        self._sim_out_event_q = Queue()
        self._sim_in_event_q = Queue()
        self._sim_snapshot_ev = Event()
        self._sim_snapshot_q = Queue()

        self._sim_process = Process(target=_run_sim, args=(
            self._sim_size,
            self.config,
            self._sim_stop_ev,
            self._sim_state_q,
            self._sim_out_event_q,
            self._sim_in_event_q,
            self._sim_snapshot_ev,
            self._sim_snapshot_q,
        ))
        self._sim_process.daemon = True
        self._sim_process.start()

        Thread(target=self.__sim_communicate, daemon=True).start()

        return self._sim_process

    def stop_simulation(self):
        if self._sim_process is not None:
            self._sim_stop_ev.set()
            self._sim_process.join()
            self._sim_process = None

    def snapshot(self):
        self._sim_snapshot_ev.set()
        return self._sim_snapshot_q.get()

    def sim_event(self, type, target):
        self._sim_in_event_q.put((type, target))

    def __sim_communicate(self):
        while True:
            if self._sim_stop_ev.is_set():
                break
            if self._sim_process is None or not self._sim_process.is_alive():
                break

            self._sim_state_q.put(self.state)

            while not self._sim_out_event_q.empty():
                self._handle_event(*self._sim_out_event_q.get_nowait())

            sleep(0.05)

        self.stop_simulation()

    def _handle_event(self, type, target_name=''):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        if type == pygame.MOUSEBUTTONDOWN:
            target = self if target_name == "main" else getattr(self, target_name, None)
            try:
                target.pin.drive_low()
            except AttributeError:
                pass

        elif type == pygame.MOUSEBUTTONUP:
            if self.config.get("classname") == "Button":
                self.pin.drive_high()
            elif callable(getattr(self, 'children_gen', None)):
                for _, child in self.children_gen():
                    if child.config.get("classname") == "Button":
                        child.pin.drive_high()
