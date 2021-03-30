from pitop import Camera
from pitop.miniscreen.buttons import SelectButton
import cv2
from time import sleep
from imutils.convenience import resize

cam = Camera(format="OpenCV", flip_top_bottom=True)
directory = "images/"
button = SelectButton()
picture_count = 0

while True:
    frame = cam.get_frame()
    frame = resize(frame, width=320)
    cv2.imshow("Frame", frame)
    if button.is_pressed:
        cv2.imwrite(f'{directory}test_{picture_count}.jpg', frame)
        print(f"Frame written to file with ID: {picture_count}\n")
        picture_count += 1
        sleep(0.5)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()