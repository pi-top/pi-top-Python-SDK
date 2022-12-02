import sys
from io import BytesIO
from multiprocessing import Event, Process, Queue
from threading import Thread
from time import sleep

import pygame
from PIL import Image

from pitop.core.mixins import Recreatable, Stateful

from . import sprites as Sprites
from .events import SimEvent, SimEventTypes
from .utils import multiply_scalar


def simulate(component, scale=None, size=None):
    return Simulation(component, scale, size)


class Simulation:
    def __del__(self):
        self.stop()

    def __init__(self, component, scale=None, size=None):
        if not isinstance(component, Recreatable):
            raise Exception("Component must inherit Recreatable to be simulated")

        if not isinstance(component, Stateful):
            raise Exception("Component must inherit Stateful to be simulated")

        component_classname = component.config.get("classname")
        self._main_sprite_class = getattr(Sprites, component_classname, None)

        if not self._main_sprite_class:
            raise Exception(f"No simulation sprite defined for '{component_classname}'")

        self.component = component
        self.scale = scale or 1  # full scale is approx life size
        self.size = size

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
                self.scale,
                self.size,
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

            # handle pygame events
            while not self._out_event_q.empty():
                sim_event = self._out_event_q.get_nowait()
                self._main_sprite_class.handle_sim_event(
                    sim_event,
                    self.component,
                )

            sleep(0.05)

        self.stop()


def to_bytes(surface):
    image_string = pygame.image.tostring(surface, "RGB")
    image = Image.frombytes("RGB", surface.get_size(), bytes(image_string))
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


def _run(
    config,
    scale,
    size,
    stop_ev,
    state_q,
    out_event_q,
    in_event_q,
    snapshot_ev,
    snapshot_q,
):
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    sprite_class = getattr(Sprites, config.get("classname"))
    size = size or multiply_scalar(scale, sprite_class.Size)

    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))

    sprite_group = sprite_class.create_sprite_group(size, config, scale)

    while not stop_ev.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_ev.set()
                break

            # mouse events are dispatched to our sprite.handle_pygame_event
            # methods for UI uses, such as activating slider inputs...
            # but they are also forwarded through out_event_q for interacting
            # with the pitop components, such as for virtual PMA button presses

            elif event.type == pygame.MOUSEBUTTONUP:
                # may be relevant to any clickable sprite or component
                for sprite in sprite_group.sprites():
                    sprite.handle_pygame_event(event)
                out_event_q.put(SimEvent(SimEventTypes.MOUSE_UP))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # relevant to targeted sprite and component only
                target = None
                pos = event.pos or (0, 0)
                for sprite in sprite_group.sprites():
                    # only handle if click pos is in sprite rect
                    rect = sprite.rect
                    if (
                        rect.x <= pos[0] <= rect.x + rect.width
                        and rect.y <= pos[1] <= rect.y + rect.height
                    ):
                        sprite.handle_pygame_event(event)
                        out_event_q.put(SimEvent(SimEventTypes.MOUSE_DOWN, sprite.name))

        for sprite in sprite_group.sprites():
            if hasattr(sprite, "slider") and sprite.slider.selected:
                out_event_q.put(
                    SimEvent(
                        SimEventTypes.SLIDER_UPDATE,
                        sprite.name,
                        sprite.slider.value,
                    )
                )

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
