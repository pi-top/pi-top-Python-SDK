from pitop.oled import PTOLEDDisplay
from time import sleep

oled_screen = PTOLEDDisplay()
oled_screen.draw_multiline_text("Hello, world!")
sleep(2)
