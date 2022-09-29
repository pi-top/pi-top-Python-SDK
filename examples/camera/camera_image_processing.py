from PIL import ImageDraw
from pitop import Camera

cam = Camera()


def draw_red_cross_over_image(im):
    # Use Pillow to draw a red cross over the image
    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128, width=5)
    draw.line((0, im.size[1], im.size[0], 0), fill=128, width=5)
    return im


im = draw_red_cross_over_image(cam.get_frame())
im.show()
