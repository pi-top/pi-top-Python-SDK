from pitop.camera import Camera
import cv2

cam = Camera(format='OpenCV')


def show_image(image):
    print("Showing image")
    print(image.shape)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)


while True:
    show_image(
        cam.get_frame()
    )
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
