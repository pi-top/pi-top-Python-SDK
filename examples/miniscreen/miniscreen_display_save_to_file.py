from pitop.miniscreen import Miniscreen
from time import sleep

miniscreen = Miniscreen()

# Image provided by 'pt-project-files'
miniscreen.display_image_file("/usr/share/pt-project-files/images/rocket.gif")

sleep(2)

print("Saving to file...")
image = miniscreen.image
image.save("/home/pi/Desktop/My Miniscreen Rocket.gif")
