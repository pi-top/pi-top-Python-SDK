from pitop.miniscreen.oled import OLEDDisplay
from time import sleep

oled_display = OLEDDisplay()
oled_display.draw_multiline_text("Hello, world!")
sleep(2)
