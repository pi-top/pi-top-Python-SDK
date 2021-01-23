from pitop.miniscreen import OLED
from time import sleep

oled = OLED()
# Image provided by 'pt-project-files'
oled.display_image_file("/usr/share/pt-project-files/images/rocket.gif")
sleep(2)
oled.image.save("/home/pi/Desktop/My OLED Rocket.gif")
