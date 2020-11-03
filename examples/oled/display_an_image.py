# Example code to draw a static image to the screen

from pitop.oled import PTOLEDDisplay
from time import sleep

oled_screen = PTOLEDDisplay()
oled_screen.draw_image_file("wave.png")
sleep(2)
