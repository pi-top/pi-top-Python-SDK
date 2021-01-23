from pitop.miniscreen import OLED
from time import sleep

oled = OLED()
oled.display_multiline_text("Hello, world!")
sleep(2)
