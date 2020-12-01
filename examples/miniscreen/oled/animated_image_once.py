from pitop.miniscreen import OLED, OLEDImage

oled_display = OLED()
oled_display.set_max_fps(10)

image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif")

while not image.finished:
    oled_display.draw_image(image)
    image.next_frame()
