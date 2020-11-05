from pitop.oled import PTOLEDDisplay
from pitop.case_buttons import PTCancelButton
from time import sleep

oled_screen = PTOLEDDisplay()
cancel_button = PTCancelButton()

oled_screen.draw_multiline_text("Press cancel to exit!", font_size=22)

while not cancel_button.is_pressed:
    sleep(0.1)

oled_screen.draw_multiline_text("Bye!")
sleep(2)
