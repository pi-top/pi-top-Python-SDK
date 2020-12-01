from pitop.miniscreen import OLED
from time import sleep

oled_display = OLED()
oled_display.draw_multiline_text("Hello, world!")
sleep(2)
