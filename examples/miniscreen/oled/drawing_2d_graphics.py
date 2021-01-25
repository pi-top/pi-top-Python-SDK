# Example code showing how to draw various shapes
from pitop.miniscreen import OLED
from PIL import Image, ImageDraw, ImageFont

oled = OLED()
image = Image.new(
    oled.mode,
    oled.size,
)
canvas = ImageDraw.Draw(image)
oled.set_max_fps(1)


def clear():
    canvas.rectangle(oled.bounding_box, fill=0)


print("Drawing an arc")
canvas.arc(oled.bounding_box, 0, 180, fill=1, width=1)
oled.display_image(image)

clear()

print("Drawing an image")
# Image provided by 'pt-project-files'
# Note: this is an animated file, but this approach will only show the first frame
demo_image = Image.open("/usr/share/pt-project-files/images/rocket.gif").convert("1")
canvas.bitmap((0, 0), demo_image, fill=1)
oled.display_image(image)

clear()

print("Drawing a chord")
canvas.chord(oled.bounding_box, 0, 180, fill=1)
oled.display_image(image)

clear()

print("Drawing an ellipse")
canvas.ellipse(oled.bounding_box, fill=1)
oled.display_image(image)

clear()

print("Drawing a line")
canvas.line(oled.bounding_box, fill=1)
oled.display_image(image)

clear()

print("Drawing a pieslice")
canvas.pieslice(oled.bounding_box, 0, 180, fill=1)
oled.display_image(image)

clear()

print("Drawing a point")
canvas.point(oled.bounding_box, fill=1)
oled.display_image(image)

clear()

print("Drawing a polygon")
canvas.polygon(oled.bounding_box, fill=1)
oled.display_image(image)

clear()

print("Drawing a rectangle")
canvas.rectangle(oled.bounding_box, fill=1)
oled.display_image(image)

clear()

print("Drawing some text")
canvas.multiline_text(
    (0, 0),
    "Hello World!",
    font=ImageFont.truetype("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", size=25),
    fill=1
)
oled.display_image(image)
