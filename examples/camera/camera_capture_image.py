from pitop import Camera
from pitop.miniscreen.buttons import SelectButton
import cv2
from time import sleep
from imutils.convenience import resize
from pitop.camera.camera_calibration.load_parameters import load_camera_cal

cam = Camera(format="OpenCV", flip_top_bottom=True)
directory = "images/"
button = SelectButton()
mtx, dist = load_camera_cal()
picture_count = 0

while True:
    frame = cam.get_frame()
    undistorted_frame = cv2.undistort(frame, mtx, dist, None, mtx)
    resized_frame = resize(undistorted_frame, width=320)

    cv2.imshow("Frame", undistorted_frame)
    if button.is_pressed:
        cv2.imwrite(f'{directory}test_{picture_count}.jpg', frame)
        print(f"Frame written to file with ID: {picture_count}\n")
        picture_count += 1
        sleep(0.5)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
