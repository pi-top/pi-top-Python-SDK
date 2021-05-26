from pitop import Pitop, DriveController, PincerController, Camera, NavigationController
from pitop.processing.algorithms import BallDetector
from signal import pause
from time import sleep


def assemble_robot():
    robot = Pitop()

    robot.add_component(Camera(resolution=(640, 480), rotate_angle=90))
    robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
    robot.add_component(PincerController())
    robot.add_component(NavigationController(drive_controller=robot.drive), name="navigate")

    return robot


def capture_ball():
    global ball_captured
    robot.pincers.close()
    ball_captured = True
    sleep(1)


def release_ball():
    global ball_captured
    robot.pincers.open()
    ball_captured = False
    sleep(1)


def retrieve_ball():
    capture_ball()
    robot.navigate.go_to(position=[-0.1, 0], angle=180).wait()
    release_ball()
    robot.navigate.go_to(position=[0, 0], angle=0, backwards=True).wait()


def follow_ball(center, radius):
    x, y = center

    if radius > ball_capture_radius:
        retrieve_ball()
        return

    forward_speed_scaler = 1 - (radius / max_rectangle_width)
    forward_speed = FORWARD_SPEED_MAX * forward_speed_scaler

    robot.drive.forward(forward_speed, hold=True)

    turn_speed_scaler = abs(x / x_max)
    turn_speed = TURN_SPEED_MAX * turn_speed_scaler

    if x < 0:
        robot.drive.left(turn_speed)
    elif x > 0:
        robot.drive.right(turn_speed)
    elif x == 0:
        robot.drive.stop_rotation()


def track_ball(frame):
    detected_balls = ball_detector(frame, color="green")

    green_ball = detected_balls.green

    if green_ball.found:
        follow_ball(center=green_ball.center, radius=green_ball.radius)
    else:
        robot.drive.stop()


robot = assemble_robot()
robot.pincers.calibrate()
robot.pincers.open()

ball_detector = BallDetector()

FORWARD_SPEED_MAX = 1.0  # You can modify this speed if you want
TURN_SPEED_MAX = 0.25  # You can modify this speed if you want

x_max = 160
max_rectangle_width = 330
max_rectangle_height = 240

ball_capture_radius = 100
ball_captured = False

robot.camera.on_frame = track_ball

pause()
