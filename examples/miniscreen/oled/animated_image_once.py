from pitop.miniscreen import OLED
from PIL import Image, ImageSequence

oled = OLED()
oled.set_max_fps(10)

# Image provided by 'pt-project-files'
rocket = Image.open("/usr/share/pt-project-files/images/rocket.gif")

for frame in ImageSequence.Iterator(rocket):
    oled.display_image(frame)
