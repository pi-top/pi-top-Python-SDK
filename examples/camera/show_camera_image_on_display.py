from pitop.camera import Camera
from cv2 import imshow
from time import sleep


def show_im(im):
    print("Showing image")
    imshow('Camera stream', im)


cam = Camera()
cam.format = "OpenCV"

print("Camera stream starting...")
cam.on_frame = show_im

sleep(60)

print("Camera stream stopped")
