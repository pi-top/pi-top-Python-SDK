from pitop import Camera
from time import sleep
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()

cam = Camera(format='OpenCV')


def show_gray_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)
    cv2.waitKey(1)  # Necessary to show image


# Use callback function for 60s
cam.on_frame = show_gray_image
sleep(60)


# Use get_frame indefinitely
try:
    while True:
        show_gray_image(cam.get_frame())

except KeyboardInterrupt:
    cv2.destroyAllWindows()
