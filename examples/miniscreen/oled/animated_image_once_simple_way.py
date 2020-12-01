from pitop.miniscreen import OLED, OLEDImage

oled = OLED()
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
oled.play_animated_image(image)
