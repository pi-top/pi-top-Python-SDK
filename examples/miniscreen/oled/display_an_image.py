# Example code to draw a static image to the screen

from pitop.miniscreen import OLED
from time import sleep

oled = OLED()
oled.draw_image_file("wave.png")
sleep(2)
