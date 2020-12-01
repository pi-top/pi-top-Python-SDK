from pitop.miniscreen import OLED
from PIL import Image

oled = OLED()
image = Image.open("/usr/share/pt-project-files/images/rocket.gif")
oled.play_animated_image(image)
