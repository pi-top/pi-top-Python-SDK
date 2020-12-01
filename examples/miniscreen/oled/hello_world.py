from pitop.miniscreen import OLED
from time import sleep

oled = OLED()
oled.draw_multiline_text("Hello, world!")
sleep(2)
