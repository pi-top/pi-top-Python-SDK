from ptoled import PTOLEDDisplay, OLEDImage
from time import sleep

ptoled = PTOLEDDisplay()
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
ptoled.play_animated_image(image)
