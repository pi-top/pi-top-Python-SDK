from pitop import Pitop
from PIL import Image

pitop = Pitop()
miniscreen = pitop.miniscreen

# Image provided by 'pt-project-files'
rocket = Image.open("/usr/share/pt-project-files/images/rocket.gif")

miniscreen.play_animated_image(rocket)
