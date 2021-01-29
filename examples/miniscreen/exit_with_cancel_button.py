from pitop.miniscreen import Miniscreen
from pitop.miniscreen import CancelButton
from time import sleep

miniscreen = Miniscreen()
cancel_button = CancelButton()

miniscreen.display_multiline_text("Press cancel to exit!", font_size=22)

while not cancel_button.is_pressed:
    sleep(0.1)

miniscreen.display_multiline_text("Bye!")
sleep(2)
