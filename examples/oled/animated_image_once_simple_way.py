from pitop.oled import PTOLEDDisplay, OLEDImage
from time import sleep

ptoled = PTOLEDDisplay()
ptoled.set_max_fps(10)

image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
ptoled.play_animated_image(image)
