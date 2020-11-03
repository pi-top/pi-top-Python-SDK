from pitop.oled import PTOLEDDisplay, OLEDImage
from time import sleep

ptoled = PTOLEDDisplay()
ptoled.set_max_fps(10)

# Set image to loop
image = OLEDImage("/usr/share/pt-project-files/images/rocket.gif", loop=True)

# run animation loop in background by setting `background` to True
ptoled.play_animated_image(image, background=True)

# print 0-99 while the animation is running in the background
for x in range(100):
    print(x)
    sleep(0.1)

# stop animation
ptoled.stop_animated_image()
