from PIL import Image
from time import sleep

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
    font_size=15)
sleep(2)


# Configure buttons to do something
keep_running = True


def display_gif_and_exit():
    # Load image
    image = Image.open("/usr/share/pt-project-files/images/rocket.gif")
    pitop.miniscreen.play_animated_image(image)
    pitop.miniscreen.display_text("Bye!")
    sleep(2)
    global keep_running
    keep_running = False


pitop.select_button.when_pressed = display_gif_and_exit
pitop.cancel_button.when_pressed = display_gif_and_exit
pitop.up_button.when_pressed = display_gif_and_exit
pitop.down_button.when_pressed = display_gif_and_exit

pitop.miniscreen.display_multiline_text("Press any\nbutton...")

# Sleep until `display_gif_and_exit` runs
while keep_running:
    sleep(0.3)
