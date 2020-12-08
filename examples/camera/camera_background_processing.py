from pitop.camera import Camera, pil_to_opencv
from PIL import ImageDraw
import cv2
from signal import pause

cam = Camera()


def show_image_with_cross(im):
    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128)
    draw.line((0, im.size[1], im.size[0], 0), fill=128)
    cv2.imshow('crossed', pil_to_opencv(im))
    cv2.waitKey(1)


# send every other frame to our processing function
cam.start_handling_frames(show_image_with_cross, frame_interval=2)

# image processing is not blocking to keep this alive so use signal.pause
pause()
