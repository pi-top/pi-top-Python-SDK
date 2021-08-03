from PIL import Image
from pitop import Pitop

pitop = Pitop()
miniscreen = pitop.miniscreen

rocket = Image.open("/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif")

miniscreen.play_animated_image(rocket)
