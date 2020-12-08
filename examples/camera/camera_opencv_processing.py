from pitop.camera import Camera
import numpy as np
import cv2

cam = Camera()

while True:
    image = cam.get_frame()
    cv_image = np.asarray(image)
    negative = cv2.bitwise_not(cv_image)
    cv2.imshow(negative)
