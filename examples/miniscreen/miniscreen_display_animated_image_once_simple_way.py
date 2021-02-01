from pitop.miniscreen import Miniscreen
from PIL import Image

miniscreen = Miniscreen()

# Image provided by 'pt-project-files'
rocket = Image.open("/usr/share/pt-project-files/images/rocket.gif")

miniscreen.play_animated_image(rocket)
