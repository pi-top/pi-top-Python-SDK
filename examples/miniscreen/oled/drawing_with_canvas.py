# Example code showing how to draw various shapes

from pitop.miniscreen import OLED
from PIL import Image

oled = OLED()
oled.set_max_fps(1)
canvas = oled.canvas
canvas.set_font_size(25)

print("Drawing an arc")
canvas.clear()
canvas.arc(canvas.get_bounding_box(), 0, 180)
oled.draw()

print("Drawing an image")
canvas.clear()
# Image provided by 'pt-project-files'
demo_image = Image.open("/usr/share/pt-project-files/images/rocket.gif")
canvas.image(canvas.top_left(), demo_image)
oled.draw()

print("Drawing a chord")
canvas.clear()
canvas.chord(canvas.get_bounding_box(), 0, 180)
oled.draw()

print("Drawing an ellipse")
canvas.clear()
canvas.ellipse(canvas.get_bounding_box())
oled.draw()

print("Drawing a line")
canvas.clear()
canvas.line(canvas.get_bounding_box())
oled.draw()

print("Drawing a pieslice")
canvas.clear()
canvas.pieslice(canvas.get_bounding_box(), 0, 180)
oled.draw()

print("Drawing a point")
canvas.clear()
canvas.point(canvas.get_bounding_box())
oled.draw()

print("Drawing a polygon")
canvas.clear()
canvas.polygon(canvas.get_bounding_box())
oled.draw()

print("Drawing a rectangle")
canvas.clear()
canvas.rectangle(canvas.get_bounding_box())
oled.draw()

print("Drawing some text")
canvas.clear()
canvas.multiline_text(canvas.top_left(), "Hello World!")
oled.draw()
