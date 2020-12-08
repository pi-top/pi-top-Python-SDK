from pitop.camera import Camera
import cv2

cam = Camera()

while True:
    image = cam.get_frame(opencv=True)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
