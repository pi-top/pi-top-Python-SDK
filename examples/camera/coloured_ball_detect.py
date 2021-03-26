from pitop.camera import Camera
from pitop.processing.algorithms import process_frame_for_ball
from signal import pause
import cv2


def process_frame(frame):
    ball_data = process_frame_for_ball(frame, colours='red', image_return_format="OpenCV")
    if ball_data.center is not None:
        center = ball_data.center
        print(f'Center: {center} | Radius: {ball_data.radius}')
    cv2.imshow("Image", ball_data.robot_view)
    cv2.waitKey(1)


camera = Camera(rotate_angle=90)
camera.on_frame = process_frame

pause()
