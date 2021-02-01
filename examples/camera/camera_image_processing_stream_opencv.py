from pitop.camera import Camera
import cv2
from time import sleep

cam = Camera(format='OpenCV')


def show_gray_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)
    cv2.waitKey(1)  # Necessary to show image


# Use callback function
cam.on_frame = show_gray_image
sleep(60)


# Use get_frame
while True:
    show_gray_image(cam.get_frame())


cv2.destroyAllWindows()
