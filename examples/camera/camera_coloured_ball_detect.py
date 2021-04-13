from os import environ
from pitopcommon.current_session_info import get_first_display
from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
from signal import pause
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()

environ["DISPLAY"] = get_first_display()


def process_frame(frame):
    balls = ball_detector.detect(frame, colour=("red", "green", "blue"))

    # Get data for red ball
    red_ball = ball.red

    # Get data for green ball
    green_ball = ball.green

    # Get data for blue ball
    blue_ball = ball.blue

    print("--------- FOUND DATA -----------")
    print(f"R: {red_ball.found} | G: {green_ball.found} | B: {blue_ball.found} \n")

    print("--------- CENTER DATA ----------")
    print(f"R: {red_ball.center} | G: {green_ball.center} | B: {blue_ball.center} \n")

    print("--------- RADIUS DATA ----------")
    print(f"R: {red_ball.radius} | G: {green_ball.radius} | B: {blue_ball.radius} \n")
    print("\n")

    cv2.imshow("Image", ball.robot_view)
    cv2.waitKey(1)


ball_detector = BallDetector(input_format="OpenCV", output_format="OpenCV")
camera = Camera(format="OpenCV")
camera.on_frame = process_frame

pause()
