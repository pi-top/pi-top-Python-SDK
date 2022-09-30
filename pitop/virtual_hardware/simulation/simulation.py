import sys
from io import BytesIO
from multiprocessing import Event, Process, Queue
from threading import Thread
from time import sleep

import pygame
from PIL import Image

from pitop.core.mixins import Recreatable, Stateful

from . import sprites as Sprites


def simulate(component):
    return Simulation(component)


class Simulation:
    def __del__(self):
        self.stop()

    def __init__(self, component):
        if not isinstance(component, Recreatable):
            raise Exception("Component must inherit Recreatable to be simulated")

        if not isinstance(component, Stateful):
            raise Exception("Component must inherit Stateful to be simulated")

        component_classname = component.config.get("classname")
        self._main_sprite_class = getattr(Sprites, component_classname, None)

        if not self._main_sprite_class:
            raise Exception(f"No simulation sprite defined for '{component_classname}'")

        self.component = component

        self._stop_ev = Event()
        self._state_q = Queue()
        self._out_event_q = Queue()
        self._in_event_q = Queue()
        self._snapshot_ev = Event()
        self._snapshot_q = Queue()

        self._process = Process(
            target=_run,
            args=(
                self.component.config,
                self._stop_ev,
                self._state_q,
                self._out_event_q,
                self._in_event_q,
                self._snapshot_ev,
                self._snapshot_q,
            ),
        )
        self._process.daemon = True
        self._process.start()

        Thread(target=self.__communicate, daemon=True).start()

    def stop(self):
        if getattr(self, "_process", None):
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
                type, target_name = self._out_event_q.get_nowait()
                self._main_sprite_class.handle_event(type, target_name, self.component)

            sleep(0.05)

        self.stop()


def to_bytes(surface):
    image_string = pygame.image.tostring(surface, "RGB")
    image = Image.frombytes("RGB", surface.get_size(), bytes(image_string))
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


def _run(config, stop_ev, state_q, out_event_q, in_event_q, snapshot_ev, snapshot_q):
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    sprite_class = getattr(Sprites, config.get("classname"))
    size = sprite_class.Size

    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))

    sprite_group = sprite_class.create_sprite_group(size, config)

    OUTBOUND_EVENTS = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]

    while not stop_ev.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_ev.set()
                break
            elif event.type in OUTBOUND_EVENTS:
                target_name = None
                if hasattr(event, "pos"):
                    for sprite in sprite_group.sprites():
                        rect = sprite.rect
                        if (
                            rect.x <= event.pos[0] <= rect.x + rect.width
                            and rect.y <= event.pos[1] <= rect.y + rect.height
                        ):
                            target_name = sprite.name
                            break
                out_event_q.put((event.type, target_name))

        while not in_event_q.empty():
            type, target_name = in_event_q.get_nowait()
            target = [s for s in sprite_group.sprites() if s.name == target_name]
            if not len(target):
                continue
            pos = (target[0].rect.x, target[0].rect.y)
            event = pygame.event.Event(
                type, {"pos": pos, "button": 1, "touch": False, "window": None}
            )
            pygame.event.post(event)

        if snapshot_ev.is_set():
            snapshot_q.put(to_bytes(screen))
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
