from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
from signal import pause
import cv2


def process_frame(frame):
    balls = ball_detector.detect(frame, colour=("red", "green", "blue"))

    red_ball = balls.red
    print(f'Red ball center: {red_ball.center}')

    green_ball = balls.green
    print(f'Green ball center: {green_ball.center}')

    blue_ball = balls.blue
    print(f'Blue ball center: {blue_ball.center}\n')

    cv2.imshow("Image", balls.robot_view)
    cv2.waitKey(1)


ball_detector = BallDetector(input_format="OpenCV", output_format="OpenCV")
camera = Camera(format="OpenCV")
camera.on_frame = process_frame

pause()
