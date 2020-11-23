# Example code to draw a static image to the screen

from pitop.miniscreen.oled import OLEDDisplay
from time import sleep

oled_display = OLEDDisplay()
oled_display.draw_image_file("wave.png")
sleep(2)
