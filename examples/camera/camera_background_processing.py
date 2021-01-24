from pitop.core import ImageFunctions
from pitop.camera import Camera
from PIL import ImageDraw
import cv2
from signal import pause

cam = Camera()


def show_image_with_cross(im):
    # Use Pillow to draw a red cross over the image
    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128)
    draw.line((0, im.size[1], im.size[0], 0), fill=128)

    # Use OpenCV to display the image in a desktop window
    cv2.imshow('crossed', ImageFunctions.pil_to_opencv(im))
    cv2.waitKey(1)  # this call is necessary to ensure the frame is displayed


# Register our callback to process camera frames, skipping every other frame
cam.start_handling_frames(show_image_with_cross, frame_interval=2)

# As our image processing is not blocking, use signal.pause to keep running
pause()
