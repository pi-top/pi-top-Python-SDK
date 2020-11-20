from pitop.miniscreen.oled import PTOLEDDisplay, OLEDImage

ptoled = PTOLEDDisplay()
ptoled.set_max_fps(10)

image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")

while not image.finished:
    ptoled.draw_image(image)
    image.next_frame()
