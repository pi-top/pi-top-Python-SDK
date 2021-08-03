from PIL import Image, ImageDraw, ImageFont
from pitop import Pitop

pitop = Pitop()
miniscreen = pitop.miniscreen
image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)
canvas = ImageDraw.Draw(image)
miniscreen.set_max_fps(1)


def clear():
    canvas.rectangle(miniscreen.bounding_box, fill=0)


print("Drawing an arc")
canvas.arc(miniscreen.bounding_box, 0, 180, fill=1, width=1)
miniscreen.display_image(image)

clear()

print("Drawing an image")
# Note: this is an animated file, but this approach will only show the first frame
demo_image = Image.open(
    "/usr/lib/python3/dist-packages/pitop/miniscreen/images/rocket.gif"
).convert("1")
canvas.bitmap((0, 0), demo_image, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a chord")
canvas.chord(miniscreen.bounding_box, 0, 180, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing an ellipse")
canvas.ellipse(miniscreen.bounding_box, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a line")
canvas.line(miniscreen.bounding_box, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a pieslice")
canvas.pieslice(miniscreen.bounding_box, 0, 180, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a point")
canvas.point(miniscreen.bounding_box, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a polygon")
canvas.polygon(miniscreen.bounding_box, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing a rectangle")
canvas.rectangle(miniscreen.bounding_box, fill=1)
miniscreen.display_image(image)

clear()

print("Drawing some text")
canvas.text((0, 0), "Hello\nWorld!", font=ImageFont.load_default(), fill=1)
miniscreen.display_image(image)
