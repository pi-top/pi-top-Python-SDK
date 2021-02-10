from pitop import Miniscreen
from PIL import Image, ImageSequence

miniscreen = Miniscreen()

# Image provided by 'pt-project-files'
rocket = Image.open("/usr/share/pt-project-files/images/rocket.gif")

for frame in ImageSequence.Iterator(rocket):
    miniscreen.display_image(frame)
