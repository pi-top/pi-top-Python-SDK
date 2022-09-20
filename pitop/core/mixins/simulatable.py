from time import sleep
from queue import Queue
from threading import Thread, Event as ThreadEvent
from multiprocessing import Process, Pipe, Event as ProcessEvent
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


def _run_sim(size, config, stop_event, conn):
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    width, height = size
    screen = pygame.display.set_mode([width, height])
    screen.fill((255, 255, 255))

    exit_code = 0

    sprite_group = _create_sprite_group(size, config)
    if not sprite_group:
        stop_event.set()
        exit_code = 1

    while not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
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
                        conn.send(("event", { "type": event.type, "target": sprite.name }))
            elif event.type == pygame.MOUSEBUTTONUP:
                conn.send(("event", { "type": event.type, "dict": event.dict }))

        while conn.poll(0):
            msg = conn.recv()
            type, data = msg
            if type == "event":
                type, target_name = data
                target = [s for s in sprite_group.sprites() if s.name == target_name]
                if not len(target):
                    continue
                pos = (target[0].rect.x, target[0].rect.y)
                event = pygame.event.Event(type, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
                pygame.event.post(event)

            elif type == "snapshot":
                pygame.image.save(screen, "temp_snapshot.png")
                snapshot = to_bytes(Image.open("temp_snapshot.png"))
                conn.send(("snapshot", snapshot))
                os.remove("temp_snapshot.png")

            elif type == "state":
                for sprite in sprite_group.sprites():
                    if sprite.name == "main":
                        sprite.state = data
                    else:
                        sprite.state = data.get(sprite.name)

        sprite_group.update()
        sprite_group.draw(screen)
        pygame.display.flip()
        clock.tick(20)

    # Don't pygame.quit() - isn't needed and can cause X server to crash
    conn.close()
    sys.exit(exit_code)


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


class PitopSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = pygame.image.load(Images.Pitop)
        self.rect = self.image.get_rect()


class LEDSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.color = config.get("color", "red")
        self.image = pygame.image.load(getattr(Images, f"LED_{self.color}_off"))
        self.rect = self.image.get_rect()

    def update(self):
        if self.state and self.state.get("value", False):
            self.image = pygame.image.load(getattr(Images, f"LED_{self.color}_on"))
        else:
            self.image = pygame.image.load(getattr(Images, f"LED_{self.color}_off"))


class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = pygame.image.load(Images.Button)
        self.rect = self.image.get_rect()

    def update(self):
        if self.state and self.state.get("is_pressed", False):
            self.image = pygame.image.load(Images.Button_pressed)
        else:
            self.image = pygame.image.load(Images.Button)


class Simulatable:
    """Represents an object that can be simulated on a digital canvas."""

    def __init__(self, size=DEFAULT_SIZE):
        # TODO must be Recreatable and Stateful
        self._sim_size = size

        self._sim_snapshot = None
        self._sim_snapshot_request = ThreadEvent()
        self._sim_snapshot_received = ThreadEvent()
        self._sim_event_queue = Queue()

        self._sim_stop_event = ProcessEvent()

        self._sim_process = None

    def __del__(self):
        # TODO what about when this is overridden?
        self.stop_simulation()

    def simulate(self):
        self.stop_simulation()

        parent_conn, child_conn = Pipe()

        self._sim_process = Process(target=_run_sim, args=(
            self._sim_size,
            self.config,
            self._sim_stop_event,
            child_conn,
        ))
        self._sim_process.daemon = True
        self._sim_process.start()

        Thread(target=self.__sim_communicate, args=(parent_conn,), daemon=True).start()

    def stop_simulation(self):
        if self._sim_process is not None:
            self._sim_stop_event.set()
            self._sim_process.join()
            self._sim_process = None

        self._sim_stop_event.clear()
        self._sim_snapshot_request.clear()
        self._sim_snapshot_received.clear()

    def snapshot(self):
        self._sim_snapshot_request.set()
        self._sim_snapshot_received.wait()
        self._sim_snapshot_received.clear()
        return self._sim_snapshot

    def sim_event(self, type, target):
        self._sim_event_queue.put((type, target))

    def __sim_communicate(self, conn):
        while True:
            if self._sim_stop_event.is_set():
                break
            if self._sim_process is None or not self._sim_process.is_alive():
                break

            try:
                conn.send(("state", self.state))
            except (BrokenPipeError, ConnectionResetError):
                break

            while not self._sim_event_queue.empty():
                event = self._sim_event_queue.get_nowait()
                conn.send(("event", event))

            if self._sim_snapshot_request.is_set():
                try:
                    conn.send(("snapshot", None))
                except (BrokenPipeError, ConnectionResetError):
                    break
                self._sim_snapshot_request.clear()

            while conn.poll(0):
                msg = conn.recv()
                type, data = msg
                if type == "snapshot":
                    self._sim_snapshot = data
                    self._sim_snapshot_received.set()
                elif type == "event":
                    self._handle_event(data)

            sleep(0.05)

        conn.close()
        self.stop_simulation()

    def _handle_event(self, event):
        if not is_virtual_hardware():
            print("Ignoring virtual input while physcial hardware is enabled")
            return

        type = event.get("type")

        if type == pygame.MOUSEBUTTONDOWN:
            target_name = event.get("target")
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
