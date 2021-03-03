from pitop import Pitop
from PIL import Image
from time import sleep

pitop = Pitop()
miniscreen = pitop.miniscreen

# Set image to loop
# Image provided by 'pt-project-files'
image = Image.open("/usr/share/pt-project-files/images/rocket.gif")

# Run animation loop in background by setting `background` to True
miniscreen.play_animated_image(image, background=True, loop=True)


# Do stuff while showing image
print("Counting to 100 while showing animated image on miniscreen...")

for i in range(100):
    print('\r{}'.format(i), end='', flush=True)
    sleep(0.2)

print('\rFinished!')

# Stop animation
miniscreen.stop_animated_image()
