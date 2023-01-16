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

        # for a component to be simulated it must have a Sprite class defined
        # with the same classname as the component class
        component_classname = component.config.get("classname")
        self._main_sprite_class = getattr(Sprites, component_classname, None)

        if not self._main_sprite_class:
            raise Exception(f"No simulation sprite defined for '{component_classname}'")

        self.component = component
        self.scale = scale or 1  # full scale is approx life size
        self.size = size

        # communication channels between main process and sim
        self._stop_ev = Event()  # stopping this simulation
        self._config_q = Queue()  # sending component config updates into sim
        self._state_q = Queue()  # sending component state updates into sim
        self._out_event_q = Queue()  # sending sim events to components
        self._in_event_q = Queue()  # artificially firing pygame events (tests)
        self._snapshot_ev = Event()  # requesting sim snapshot images
        self._snapshot_q = Queue()  # returning snapshot images

        # pygame must be run in another process as it is designed to use the
        # main thread, and is particularly not suited to running multiple
        # pygame applications in one process
        self._process = Process(
            target=_run,
            args=(
                self.component.config,
                self.scale,
                self.size,
                self._stop_ev,
                self._config_q,
                self._state_q,
                self._out_event_q,
                self._in_event_q,
                self._snapshot_ev,
                self._snapshot_q,
            ),
        )
        self._process.daemon = True
        self._process.start()

        # thread for interprocess communication with the sim, which is used to
        # regularly synchronise the state of the components with their sprites
        # in the simulation and dispatch input events from inside the sim
        Thread(target=self.__communicate, daemon=True).start()

    def stop(self):
        if getattr(self, "_process", None):
            self._stop_ev.set()
            self._process.join()
            self._process = None

    def snapshot(self):
        # request an image of the sim and wait for it to arrive on the queue
        self._snapshot_ev.set()
        return self._snapshot_q.get()

    def event(self, type, target):
        # send a pygame event into the sim to simulate interactions for tests
        self._in_event_q.put((type, target))

    def __communicate(self):
        # store config as a string (not reference) to easily check if it's changed
        str_config = str(self.component.config)

        while True:
            if self._stop_ev.is_set():
                break

            if self._process is None or not self._process.is_alive():
                break

            # update sim with current state of simulated component
            self._state_q.put(self.component.state)

            # update sim with current config only if it's changed
            if str(self.component.config) != str_config:
                str_config = str(self.component.config)
                self._config_q.put(self.component.config)

            # handle events produced by the sim which affect our simulated
            # component (eg PMA Button presses, sensor slider updates)
            while not self._out_event_q.empty():
                sim_event = self._out_event_q.get_nowait()
                self._main_sprite_class.handle_sim_event(
                    sim_event,
                    self.component,
                )

            # sleep - timed to match pygame loop
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
    config_q,
    state_q,
    out_event_q,
    in_event_q,
    snapshot_ev,
    snapshot_q,
):
    # the pygame application - this should be a separate python process
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()

    sprite_class = getattr(Sprites, config.get("classname"))
    size = size or multiply_scalar(scale, sprite_class.Size)

    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))

    # create our sprites based on the simulated component's config
    sprite_group, main_sprite = sprite_class.create_sprite_group(size, config, scale)

    while not stop_ev.is_set():
        # handle pygame events eg UI
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

        # send out postion update events for selected sliders
        for sprite in sprite_group.sprites():
            if hasattr(sprite, "slider") and sprite.slider.selected:
                out_event_q.put(
                    SimEvent(
                        SimEventTypes.SLIDER_UPDATE,
                        sprite.name,
                        sprite.slider.value,
                    )
                )

        # handle incoming simulated ui events
        while not in_event_q.empty():
            # find which sprite matches the target_name and translate to target
            # the event at that sprite's position in the simulation
            type, target_name = in_event_q.get_nowait()
            target = [s for s in sprite_group.sprites() if s.name == target_name]
            if not len(target):
                continue
            pos = (target[0].rect.x, target[0].rect.y)
            event = pygame.event.Event(
                type, {"pos": pos, "button": 1, "touch": False, "window": None}
            )
            pygame.event.post(event)

        # respond to screenshot requests
        if snapshot_ev.is_set():
            snapshot_q.put(to_bytes(screen))
            snapshot_ev.clear()

        # check changes to component config eg newly added sprites
        while not config_q.empty():
            new_config = config_q.get_nowait()
            components = new_config.get("components", {})

            sprite_names = [sprite.name for sprite in sprite_group.sprites()]

            for component in components.values():
                if component.get("name") not in sprite_names:
                    component_sprite = main_sprite.create_child_sprite(component, scale)
                    sprite_group.add(component_sprite)

        # forward inbound component state updates
        while not state_q.empty():
            # provide sprites with relevant part of the component state tree
            state = state_q.get_nowait()
            for sprite in sprite_group.sprites():
                if sprite.name == "main":
                    sprite.state = state
                else:
                    sprite.state = state.get(sprite.name)

        # draw
        sprite_group.update()
        sprite_group.draw(screen)
        pygame.display.flip()

        # sleep - timed to match controlling thread
        clock.tick(20)

    # Don't pygame.quit() - isn't needed and can cause X server to crash
    sys.exit()
