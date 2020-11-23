from pitop.miniscreen.oled import OLEDDisplay, OLEDImage

oled_display = OLEDDisplay()
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
oled_display.play_animated_image(image)
