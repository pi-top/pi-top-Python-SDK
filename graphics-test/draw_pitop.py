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
# can.configure(bg="blue")

pitop_pil_image = Image.open("Pitop.png")
pitop_tk_image = ImageTk.PhotoImage(pitop_pil_image)
pitop_sprite = can.create_image(pitop_pos[0], pitop_pos[1], image=pitop_tk_image)


led_on = False
led_pil_image = None

def draw_led():
    global led_tk_image # NB need to keep this reference around!
    if led_on:
        led_pil_image = Image.open("LED_green_on.png")
    else:
        led_pil_image = Image.open("LED_green_off.png")
    led_tk_image = ImageTk.PhotoImage(led_pil_image)
    led_sprite = can.create_image(led_pos[0], led_pos[1], image=led_tk_image)

draw_led()

button_pil_image = Image.open("Button.png")
button_tk_image = ImageTk.PhotoImage(button_pil_image)


def virtual_click():
    global led_on
    print('click!')
    led_on = not led_on
    draw_led()
sprite = tkinter.Button(tk, text='hi', image=button_tk_image, command=virtual_click, borderwidth=0)
sprite.place(x=led_pos[0] - 25, y=led_pos[1] + 25)

tk.mainloop()
