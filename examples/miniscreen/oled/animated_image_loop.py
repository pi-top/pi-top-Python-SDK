from pitop.miniscreen import OLED
from PIL import Image, ImageSequence

oled = OLED()
oled.set_max_fps(10)

rocket = Image.open("/usr/share/pt-project-files/images/rocket.gif")

while True:
    for frame in ImageSequence.Iterator(rocket):
        oled.draw_image(frame)
