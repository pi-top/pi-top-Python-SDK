from ptoled import PTOLEDDisplay, OLEDImage

ptoled = PTOLEDDisplay()
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")
ptoled.play_animated_image(image)
