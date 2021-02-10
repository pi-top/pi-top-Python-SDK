from pitop import Miniscreen
from time import sleep

miniscreen = Miniscreen()
miniscreen.display_multiline_text("Press cancel to exit!", font_size=22)

while not miniscreen.cancel_button.is_pressed:
    sleep(0.1)

miniscreen.display_multiline_text("Bye!")
sleep(2)
