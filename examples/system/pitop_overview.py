from time import sleep

from PIL import Image
from pitop import Pitop

# Set up pi-top
pitop = Pitop()

# Say hi!
pitop.miniscreen.display_text("Hello!")
sleep(2)

# Display battery info
battery_capacity = pitop.battery.capacity
battery_charging = pitop.battery.is_charging

pitop.miniscreen.display_multiline_text(
    "Battery Status:\n"
    f"-Capacity: {battery_capacity}%\n"
    f"-Charging: {battery_charging}",
    font_size=15,
)
sleep(2)


# Configure buttons to do something
keep_running = True


def display_gif_and_exit():
    image = Image.open(
        "/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif"
    )
    pitop.miniscreen.play_animated_image(image)
    pitop.miniscreen.display_text("Bye!")
    sleep(2)
    global keep_running
    keep_running = False


pitop.miniscreen.select_button.when_pressed = display_gif_and_exit
pitop.miniscreen.cancel_button.when_pressed = display_gif_and_exit
pitop.miniscreen.up_button.when_pressed = display_gif_and_exit
pitop.miniscreen.down_button.when_pressed = display_gif_and_exit

pitop.miniscreen.display_multiline_text("Press any button...", font_size=25)

# Sleep until `display_gif_and_exit` runs
while keep_running:
    sleep(0.3)
