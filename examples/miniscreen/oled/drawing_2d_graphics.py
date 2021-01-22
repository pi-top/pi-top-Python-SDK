# Example code showing how to draw various shapes

from pitop.miniscreen import OLED
from PIL import Image, ImageDraw

oled = OLED()
oled.set_max_fps(1)
canvas = ImageDraw.Draw(oled.image)
canvas.set_font_size(25)


def clear():
    canvas.rectangle(oled.bounding_box, fill=0)


print("Drawing an arc")
clear()
canvas.arc(oled.bounding_box, 0, 180)
oled.display()

print("Drawing an image")
clear()
# Image provided by 'pt-project-files'
demo_image = Image.open("/usr/share/pt-project-files/images/rocket.gif")
canvas.image(canvas.top_left(), demo_image)
oled.display()

print("Drawing a chord")
clear()
canvas.chord(oled.bounding_box, 0, 180)
oled.display()

print("Drawing an ellipse")
clear()
canvas.ellipse(oled.bounding_box)
oled.display()

print("Drawing a line")
clear()
canvas.line(oled.bounding_box)
oled.display()

print("Drawing a pieslice")
clear()
canvas.pieslice(oled.bounding_box, 0, 180)
oled.display()

print("Drawing a point")
clear()
canvas.point(oled.bounding_box)
oled.display()

print("Drawing a polygon")
clear()
canvas.polygon(oled.bounding_box)
oled.display()

print("Drawing a rectangle")
clear()
canvas.rectangle(oled.bounding_box)
oled.display()

print("Drawing some text")
clear()
canvas.multiline_text(canvas.top_left(), "Hello World!")
oled.display()
