from pitop.miniscreen import OLED
from pitop.miniscreen import CancelButton
from time import sleep

oled = OLED()
cancel_button = CancelButton()

oled.draw_multiline_text("Press cancel to exit!", font_size=22)

while not cancel_button.is_pressed:
    sleep(0.1)

oled.draw_multiline_text("Bye!")
sleep(2)
