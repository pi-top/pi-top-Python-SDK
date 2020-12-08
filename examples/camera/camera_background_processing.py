from pitop.camera import Camera
from PIL import ImageDraw
from signal import pause

cam = Camera()


def show_image_with_cross(im):
    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128)
    draw.line((0, im.size[1], im.size[0], 0), fill=128)


# send every 100th frame to our processing function
cam.start_handling_frames(show_image_with_cross, frame_interval=100)

pause()
