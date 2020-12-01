from pitop.miniscreen import OLED, OLEDImage

oled = OLED()
oled.set_max_fps(10)

image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif", loop=True)

while True:
    oled.draw_image(image)
    image.next_frame()
