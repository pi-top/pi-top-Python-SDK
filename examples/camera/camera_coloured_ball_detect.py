from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
from signal import pause
import cv2


def process_frame(frame):
    detected_balls = ball_detector.detect(frame, color=("red", "green", "blue"))

    red_ball = detected_balls.red
    if red_ball.is_valid():
        print(f'Red ball center: {red_ball.center}')

    green_ball = detected_balls.green
    if green_ball.is_valid():
        print(f'Green ball center: {green_ball.center}')

    blue_ball = detected_balls.blue
    if blue_ball.is_valid():
        print(f'Blue ball center: {blue_ball.center}\n')

    cv2.imshow("Image", detected_balls.robot_view)
    cv2.waitKey(1)


ball_detector = BallDetector()
camera = Camera()
camera.on_frame = process_frame

pause()
