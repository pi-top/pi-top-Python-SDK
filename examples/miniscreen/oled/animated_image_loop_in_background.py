from pitop.miniscreen import Miniscreen
from PIL import Image
from time import sleep

miniscreen = Miniscreen()
miniscreen.set_max_fps(10)

# Set image to loop
# Image provided by 'pt-project-files'
image = Image.open("/usr/share/pt-project-files/images/rocket.gif")

# run animation loop in background by setting `background` to True
miniscreen.play_animated_image(image, background=True, loop=True)

# print 0-99 while the animation is running in the background
for x in range(100):
    print(x)
    sleep(0.1)

# stop animation
miniscreen.stop_animated_image()
