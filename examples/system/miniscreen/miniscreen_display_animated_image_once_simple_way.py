from pitop import Pitop
from PIL import Image

pitop = Pitop()
miniscreen = pitop.miniscreen

rocket = Image.open("/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif")

miniscreen.play_animated_image(rocket)
