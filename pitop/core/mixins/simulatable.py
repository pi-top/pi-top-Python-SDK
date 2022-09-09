from time import sleep
from threading import Thread, Event as ThreadEvent
from multiprocessing import Process, Pipe, Event as ProcessEvent
from math import cos, sin, radians, sqrt

import pygame
from PIL import Image

import pitop.common.images as Images


# this is based on the inital further-link graphics area dimensions of 720x680
# multiplied by 2 to leave plenty space around our pi-top image of 435x573
DEFAULT_SIZE = (1440, 1360)


def _run_sim(size, config, stop_event, conn):
    pygame.init()
    pygame.fastevent.init()
    clock = pygame.time.Clock()

    width, height = size
    screen = pygame.display.set_mode([width, height])
    screen.fill((255, 255, 255))

    exit_code = 0

    sprite_group, sprites = _create_sprite_group(size, config)
    if not sprite_group:
        stop_event.set()
        exit_code = 1

    while not stop_event.is_set():
        for event in pygame.fastevent.get():
            if event.type == pygame.QUIT:
                break
            # TODO move the click events here and dispatch to the correct sprite
            else:
                conn.send(("event", { "type": event.type, "dict": event.dict }))

        while conn.poll(0):
            msg = conn.recv()
            type, data = msg
            if type == "snapshot":
                pygame.image.save(screen, "temp_snapshot.png")
                snapshot = to_bytes(Image.open("temp_snapshot.png"))
                conn.send("snapshot", snapshot)
                os.remove("temp_snapshot.png")

            elif type == "state":
                for key, value in sprites.items():
                    if key == "main":
                        sprites[key].state = data
                    else:
                        components = data.get('components', {})
                        sprites[key].state = components.get(key)

        sprite_group.update()
        sprite_group.draw(screen)
        pygame.display.flip()
        clock.tick(20)

    conn.close()
    exit(exit_code)


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
    sprites = {}

    sprite = _create_sprite(config)
    if not sprite:
        return (None, None)

    # position main sprite in center
    center = int(sim_size[0] / 2), int(sim_size[1]/ 2)
    sprite.rect.x = center[0] - int(sprite.rect.width / 2)
    sprite.rect.y = center[1] - int(sprite.rect.height / 2)

    sprite_group.add(sprite)
    sprites["main"] = sprite

    sprite_centres = _generate_sprite_centres(sim_size, sprite)

    components = config.get('components', [])
    for component in components.values():
        sprite = _create_sprite(component)
        if not sprite:
            continue

        sprite_centre = sprite_centres.get(
            component.get("port_name", None), (0, 0)
        )

        sprite.rect.x = sprite_centre[0] - int(sprite.rect.width / 2)
        sprite.rect.y = sprite_centre[1] - int(sprite.rect.height / 2)

        sprite_group.add(sprite)
        sprites[component.get("name")] = sprite

    return (sprite_group, sprites)


class PitopSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.image = pygame.image.load(Images.Pitop)
        self.rect = self.image.get_rect()


class LEDSprite(pygame.sprite.Sprite):
    def __init__(self, config):
        super().__init__()

        self.config = config
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


class Simulatable:
    """Represents an object that can be simulated on a digital canvas."""

    def __init__(self, size=DEFAULT_SIZE):
        # TODO must be recreatable and stateful
        self._sim_size = size

        self._sim_snapshot = None
        self._sim_snapshot_request = ThreadEvent()
        self._sim_snapshot_received = ThreadEvent()

        self._sim_stop_event = ProcessEvent()

        self._sim_process = None

    def __del__(self):
        self.stop_simulation()

    def simulate(self):
        self.stop_simulation()
        self._sim_stop_event.clear()

        parent_conn, child_conn = Pipe()

        self._sim_process = Process(target=_run_sim, args=(
            self._sim_size,
            self.config,
            self._sim_stop_event,
            child_conn,
        )).start()

        Thread(target=self.__sim_communicate, args=(parent_conn,), daemon=True).start()

    def stop_simulation(self):
        if self._sim_process is not None:
            self._sim_stop_event.set()
            self._sim_process.join(1)

            if self._sim_process.is_alive():
                self._sim_process.kill()

            self._sim_stop_event.clear()
            self._sim_snapshot_request.clear()
            self._sim_snapshot_received.clear()
            self._sim_conn.close()
            self._sim_conn = None
            self._sim_process = None

    def snapshot(self):
        self._sim_snapshot_request.set()
        self._sim_snapshot_received.wait()
        self._sim_snapshot_received.clear()
        return self._sim_snapshot

    def __sim_communicate(self, conn):
        while not self._sim_stop_event.is_set():
            try:
                conn.send(["state", self.state])
            except BrokenPipeError:
                break


            if self._sim_snapshot_request.is_set():
                try:
                    conn.send(("snapshot", None))
                except BrokenPipeError:
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

    def _handle_event(self, event):
        pass
