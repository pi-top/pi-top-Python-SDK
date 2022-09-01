import tkinter
from threading import Event, Thread
from time import sleep

from PIL import ImageTk


class Simulatable:
    """Represents an object that can be simulated on a digital canvas."""

    def __del__(self):
        self.stop_simulation()

    def __init__(self, size=(780, 620)):
        self._sim_images = {}
        self._sim_size = size
        self._sim_root = None
        self._sim_canvas = None
        self._stop_sim = None
        self._sim_loop = None

    def simulate(self):
        self._sim_root = tkinter.Tk()

        width, height = self._sim_size
        self._sim_root.geometry(f"{width}x{height}")
        self._sim_canvas = tkinter.Canvas(self._sim_root, width=width, height=height)
        self._sim_canvas.pack()
        self._sim_root.update()

        self._create_sprites(self._sim_canvas, (0, 0))
        self.__tick()

        self._sim_loop = Thread(target=self.__main_loop, daemon=True)
        self._sim_loop.start()

    def stop_simulation(self):
        if self._stop_sim is not None:
            self._stop_sim.set()
            self._sim_root.destroy()
            self._sim_root = None
            self._sim_canvas = None

    def __tick(self):
        self._update_sprites(self._sim_canvas)
        self._sim_root.update_idletasks()
        self._sim_root.update()

    def __main_loop(self):
        self._stop_sim = Event()

        while not self._stop_sim.is_set():
            self.__tick()
            sleep(0.05)

    def _create_sprites(self, canvas, pos):
        raise NotImplementedError(
            "_create_sprites must be implemented to use `simulate`"
        )

    def _update_sprites(self, canvas):
        # some simulatable object may not need to update their sprites
        pass

    def _set_sprite_image(self, canvas, sprite=None, sprite_id=None, image=None):
        if sprite is None and sprite_id is None:
            raise Exception(
                "Either sprite or sprite_id must be provided to _set_sprite_image"
            )

        self._sim_images[sprite_id] = ImageTk.PhotoImage(image)

        if sprite is not None:
            sprite.configure(image=self._sim_images[sprite_id])
            return

        canvas.itemconfigure(sprite_id, image=self._sim_images[sprite_id])
