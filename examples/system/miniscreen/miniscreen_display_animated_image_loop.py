from pitop import Pitop
from PIL import Image, ImageSequence

pitop = Pitop()
miniscreen = pitop.miniscreen

rocket = Image.open("/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif")

while True:
    for frame in ImageSequence.Iterator(rocket):
        miniscreen.display_image(frame)
