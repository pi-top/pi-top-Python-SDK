from pitop.common.singleton import Singleton
from pitop.core.mixins import Componentable, SupportsBattery, SupportsMiniscreen

from pitop.pma import LED, Button
import pitop.common.images as Images


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
        self.sprites = {}
        tk = self.draw()
        tk.mainloop()

    def draw(self):
        global can
        global pitop_tk_image # TODO need to keep refs around

        import tkinter
        from PIL import Image, ImageTk

        width = 780;
        height = 620;
        size = width, height

        pitop_size = 250, 250
        pitop_pos = (width / 2), (height / 2)

        led_size = 50, 50
        led_pos = pitop_pos[0] + 200, pitop_pos[1] - 50

        tk = tkinter.Tk()
        tk.geometry(f'{width}x{height}')
        can = tkinter.Canvas(tk,width=width,height=height)
        can.pack()

        pitop_pil_image = Image.open(Images.Pitop)
        pitop_tk_image = ImageTk.PhotoImage(pitop_pil_image)
        pitop_sprite = can.create_image(pitop_pos[0], pitop_pos[1], image=pitop_tk_image)

        self.sprites['self'] = pitop_sprite

        for child_name in self.children:
            child = getattr(self, child_name, None)
            if isinstance(child, LED):
                pos = pitop_pos[0] + 200, pitop_pos[1] - 50 # TODO base on child.config.port

                if child.state.get('value', False):
                    pil_image = Image.open(Images.LED_green_on)
                else:
                    pil_image = Image.open(Images.LED_green_off)
                tk_image = ImageTk.PhotoImage(pil_image)
                sprite = can.create_image(pos[0], pos[1], image=tk_image)

            elif isinstance(child, Button):
                pos = pitop_pos[0] + 200, pitop_pos[1] + 50 # TODO base on child.config.port

                pil_image = Image.open(Images.Button)
                tk_image = ImageTk.PhotoImage(pil_image) # TODO might need to keep reference to this

                def virutal_click():
                    print('button click')
                    child.is_pressed = true
                    child.value = true
                    child.is_active = true
                    child._fire_events(child.pin_factory.ticks(), child.is_active)

                sprite = tkinter.Button(tk, image=tk_image, command=virtual_click, borderwidth=0)
                sprite.place(x=pos[0] - 25, y=pos[1] - 25) # pos is top left not center

            self.sprites[child_name] = sprite
        return tk

