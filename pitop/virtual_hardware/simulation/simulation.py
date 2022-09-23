from time import sleep
from threading import Thread
from multiprocessing import Process, Pipe, Queue, Event
from math import cos, sin, radians, sqrt
import sys

import pygame
from PIL import Image

from pitop.virtual_hardware import is_virtual_hardware
import pitop.virtual_hardware.simulation.sprites as Sprites
from pitop.core.mixins import Recreatable, Stateful


import os
from io import BytesIO
def to_bytes(image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

def _run(size, config, stop_ev, state_q, out_event_q, in_event_q, snapshot_ev, snapshot_q):
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
                    if not isinstance(sprite, Sprites.Button):
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
    try:
        return getattr(Sprites, config.get('classname'))(config)
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

# this is based on the inital further-link graphics area dimensions of 720x680
# multiplied by 2 to leave plenty space around our pi-top image of 435x573
PITOP_SIM_SIZE = (1560, 1240)
PMA_CUBE_SIM_SIZE = (122, 122)

sizes = {
    "Pitop": PITOP_SIM_SIZE,
    "LED": PMA_CUBE_SIM_SIZE,
    "Button": PMA_CUBE_SIM_SIZE,
}

def simulate(component):
    return Simulation(component)

class Simulation:
    def __del__(self):
        self.stop()

    def __init__(self, component, size=None):
        if not isinstance(component, Recreatable):
            raise Exception("Component must inherit Recreatable to be simulated")

        if not isinstance(component, Stateful):
            raise Exception("Component must inherit Stateful to be simulated")

        component_classname = component.config.get("classname")

        if not getattr(Sprites, component_classname, None):
            raise Exception(f"No simulation sprite defined for '{component_classname}'")

        self.component = component

        self.size = sizes.get(component_classname, PITOP_SIM_SIZE)

        self._stop_ev = Event()
        self._state_q = Queue()
        self._out_event_q = Queue()
        self._in_event_q = Queue()
        self._snapshot_ev = Event()
        self._snapshot_q = Queue()

        self._process = Process(target=_run, args=(
            self.size,
            self.component.config,
            self._stop_ev,
            self._state_q,
            self._out_event_q,
            self._in_event_q,
            self._snapshot_ev,
            self._snapshot_q,
        ))
        self._process.daemon = True
        self._process.start()

        Thread(target=self.__communicate, daemon=True).start()

    def stop(self):
        if self._process is not None:
            self._stop_ev.set()
            self._process.join()
            self._process = None

    def snapshot(self):
        self._snapshot_ev.set()
        return self._snapshot_q.get()

    def event(self, type, target):
        self._in_event_q.put((type, target))

    def __communicate(self):
        while True:
            if self._stop_ev.is_set():
                break
            if self._process is None or not self._process.is_alive():
                break

            self._state_q.put(self.component.state)

            while not self._out_event_q.empty():
                self._handle_event(*self._out_event_q.get_nowait())

            sleep(0.05)

        self.stop()

    def _handle_event(self, type, target_name=''):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        if type == pygame.MOUSEBUTTONDOWN:
            target = self.component if target_name == "main" else getattr(self.component, target_name, None)
            try:
                target.pin.drive_low()
            except AttributeError:
                pass

        elif type == pygame.MOUSEBUTTONUP:
            if self.component.config.get("classname") == "Button":
                self.component.pin.drive_high()
            elif callable(getattr(self.component, 'children_gen', None)):
                for _, child in self.component.children_gen():
                    if child.config.get("classname") == "Button":
                        child.pin.drive_high()
