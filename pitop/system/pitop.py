import tkinter
from time import sleep

from PIL import Image, ImageTk

import pitop.common.images as Images
from pitop.common.singleton import Singleton
from pitop.core.mixins import Componentable, SupportsBattery, SupportsMiniscreen
from pitop.pma import LED, Button


class Pitop(SupportsMiniscreen, SupportsBattery, Componentable, metaclass=Singleton):
    """Represents a pi-top Device.

    When creating a `Pitop` object, multiple properties will be set,
    depending on the pi-top device that it's running the code. For example, if run on
    a pi-top [4], a `miniscreen` attribute will be created as an interface to control the
    miniscreen OLED display, but that won't be available for other pi-top devices.

    The Pitop class is a Singleton. This means that only one instance per process will
    be created. In practice, this means that if in a particular project you instance a Pitop
    class in 2 different files, they will share the internal state.

    *property* miniscreen
        If using a pi-top [4], this property returns a :class:`pitop.miniscreen.Miniscreen` object, to interact with the device's Miniscreen.


    *property* oled
        Refer to `miniscreen`.


    *property* battery
        If using a pi-top with a battery, this property returns a :class:`pitop.battery.Battery` object, to interact with the device's battery.
    """

    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        Componentable.__init__(self)

    def virtualize(self):
        self.tk = tkinter.Tk()

        width, height = 780, 620
        self.tk.geometry(f"{width}x{height}")
        self.canvas = tkinter.Canvas(self.tk, width=width, height=height)
        self.canvas.pack()

        self.create_sprites(width, height)

        while True:
            sleep(0.05)
            self.draw()
            self.tk.update_idletasks()
            self.tk.update()

    def create_sprites(self, width, height):
        self.sprites = {}
        self.images = {}
        centre = (int(width / 2), int(height / 2))

        # create components
        pitop_image = ImageTk.PhotoImage(Image.open(Images.Pitop))
        pitop_sprite_id = self.canvas.create_image(
            centre[0], centre[1], image=pitop_image
        )

        self.sprites["pitop"] = pitop_sprite_id
        self.images[pitop_sprite_id] = pitop_image

        for child_name in self.children:
            child = getattr(self, child_name, None)

            if isinstance(child, LED):
                image_path = Images.LED_green_on
                if not child.state.get("value", False):
                    image_path = Images.LED_green_off

                image = ImageTk.PhotoImage(Image.open(image_path))
                sprite_id = self.canvas.create_image(
                    centre[0] + 200, centre[1] - 50, image=image
                )

                self.sprites[child_name] = sprite_id
                self.images[sprite_id] = image

            elif isinstance(child, Button):
                image = ImageTk.PhotoImage(Image.open(Images.Button))

                def button_release(_):
                    child._fire_events(child.pin_factory.ticks(), False)

                def button_press(_):
                    child._fire_events(child.pin_factory.ticks(), True)

                sprite = tkinter.Button(self.tk, image=image, borderwidth=0)

                # sprite.place uses top left instead of centre of image
                sprite.place(x=centre[0] + 200, y=centre[1] + 50)
                sprite.bind("<ButtonRelease>", button_release)
                sprite.bind("<ButtonPress>", button_press)

                sprite_id = sprite.winfo_id()
                self.sprites[child_name] = sprite_id
                self.images[sprite.winfo_id()] = image

    def draw(self):
        for child_name in self.children:
            child = getattr(self, child_name, None)

            if isinstance(child, LED):
                image_path = Images.LED_green_on
                if not child.state.get("value", False):
                    image_path = Images.LED_green_off

                self.update_image(child_name, Image.open(image_path))

    def update_image(self, child_name, image):
        sprite_id = self.sprites[child_name]
        self.images[sprite_id] = ImageTk.PhotoImage(image)
        self.canvas.itemconfigure(sprite_id, image=self.images[sprite_id])
