from pitop.miniscreen.oled import OLEDDisplay
from pitop.miniscreen.buttons import CancelButton
from time import sleep

oled_display = OLEDDisplay()
cancel_button = CancelButton()

oled_display.draw_multiline_text("Press cancel to exit!", font_size=22)

while not cancel_button.is_pressed:
    sleep(0.1)

oled_display.draw_multiline_text("Bye!")
sleep(2)
