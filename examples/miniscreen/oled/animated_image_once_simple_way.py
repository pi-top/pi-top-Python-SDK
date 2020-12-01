from pitop.miniscreen import OLED, OLEDImage

oled_display = OLED()
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
oled_display.play_animated_image(image)
