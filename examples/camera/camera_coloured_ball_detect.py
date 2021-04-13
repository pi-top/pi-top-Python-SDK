from os import environ
from pitopcommon.current_session_info import get_first_display
from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
from signal import pause
import cv2

environ["DISPLAY"] = get_first_display()


def process_frame(frame):
    balls = ball_detector.detect(frame, colour=("red", "green", "blue"))

    # Get data for red ball
    red_ball = ball.red
    print(f'Red ball center: {red_ball.center}')

    # Get data for green ball
    green_ball = ball.green
    print(f'Green ball center: {green_ball.center}')

    # Get data for blue ball
    blue_ball = ball.blue
    print(f'Blue ball center: {blue_ball.center}\n')

    cv2.imshow("Image", ball.robot_view)
    cv2.waitKey(1)


ball_detector = BallDetector(input_format="OpenCV", output_format="OpenCV")
camera = Camera(format="OpenCV")
camera.on_frame = process_frame

pause()
