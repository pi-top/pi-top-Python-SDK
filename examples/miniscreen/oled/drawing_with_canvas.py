# Example code showing how to draw various shapes

from pitop.miniscreen.oled import OLEDDisplay, OLEDImage

oled_display = OLEDDisplay()
oled_display.set_max_fps(1)
canvas = oled_display.canvas
canvas.set_font_size(25)

print("Drawing an arc")
canvas.clear()
canvas.arc(canvas.get_bounding_box(), 0, 180)
oled_display.draw()

print("Drawing an image")
canvas.clear()
demo_image = OLEDImage("demo.png")
canvas.image(canvas.top_left(), demo_image)
oled_display.draw()

print("Drawing a chord")
canvas.clear()
canvas.chord(canvas.get_bounding_box(), 0, 180)
oled_display.draw()

print("Drawing an ellipse")
canvas.clear()
canvas.ellipse(canvas.get_bounding_box())
oled_display.draw()

print("Drawing a line")
canvas.clear()
canvas.line(canvas.get_bounding_box())
oled_display.draw()

print("Drawing a pieslice")
canvas.clear()
canvas.pieslice(canvas.get_bounding_box(), 0, 180)
oled_display.draw()

print("Drawing a point")
canvas.clear()
canvas.point(canvas.get_bounding_box())
oled_display.draw()

print("Drawing a polygon")
canvas.clear()
canvas.polygon(canvas.get_bounding_box())
oled_display.draw()

print("Drawing a rectangle")
canvas.clear()
canvas.rectangle(canvas.get_bounding_box())
oled_display.draw()

print("Drawing some text")
canvas.clear()
canvas.multiline_text(canvas.top_left(), "Hello World!")
oled_display.draw()
