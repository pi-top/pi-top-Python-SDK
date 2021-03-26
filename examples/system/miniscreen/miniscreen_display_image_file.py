from pitop import Pitop
from time import sleep

pitop = Pitop()
miniscreen = pitop.miniscreen

# Image provided by 'pt-project-files'
miniscreen.display_image_file("/usr/share/pt-project-files/images/rocket.gif")

sleep(2)
