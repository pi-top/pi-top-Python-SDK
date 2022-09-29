from time import sleep

from PIL import Image
from pitop import Pitop

pitop = Pitop()
miniscreen = pitop.miniscreen

image = Image.open("/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif")

# Run animation loop in background by setting `background` to True
miniscreen.play_animated_image(image, background=True, loop=True)


# Do stuff while showing image
print("Counting to 100 while showing animated image on miniscreen...")

for i in range(100):
    print("\r{}".format(i), end="", flush=True)
    sleep(0.2)

print("\rFinished!")

# Stop animation
miniscreen.stop_animated_image()
