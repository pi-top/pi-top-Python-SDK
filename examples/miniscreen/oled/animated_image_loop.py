from pitop.miniscreen.oled import OLEDDisplay, OLEDImage

oled_display = OLEDDisplay()
oled_display.set_max_fps(10)

image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif", loop=True)

while True:
    oled_display.draw_image(image)
    image.next_frame()
