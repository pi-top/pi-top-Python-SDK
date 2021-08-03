from signal import pause

import cv2
from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector


def process_frame(frame):
    detected_balls = ball_detector(frame, color=["red", "green", "blue"])

    red_ball = detected_balls.red
    if red_ball.found:
        print(f"Red ball center: {red_ball.center}")
        print(f"Red ball radius: {red_ball.radius}")
        print(f"Red ball angle: {red_ball.angle}")
        print()

    green_ball = detected_balls.green
    if green_ball.found:
        print(f"Green ball center: {green_ball.center}")
        print(f"Green ball radius: {green_ball.radius}")
        print(f"Green ball angle: {green_ball.angle}")
        print()

    blue_ball = detected_balls.blue
    if blue_ball.found:
        print(f"Blue ball center: {blue_ball.center}")
        print(f"Blue ball radius: {blue_ball.radius}")
        print(f"Blue ball angle: {blue_ball.angle}")
        print()

    cv2.imshow("Image", detected_balls.robot_view)
    cv2.waitKey(1)


ball_detector = BallDetector()
camera = Camera(resolution=(640, 480))
camera.on_frame = process_frame

pause()
