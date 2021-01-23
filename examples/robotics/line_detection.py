from pitop import AlexRobot
from pitop.processing.algorithms.line_detect import (
    find_line,
    get_control_angle,
)

from signal import pause


# Set up logic based on line detection
def drive_based_on_frame(frame):
    centroid, robot_view = find_line(frame)
    angle = get_control_angle(centroid, robot_view)
    print(f"Target angle: {angle:.2f} deg ", end="\r")
    robot.target_lock_drive_angle(angle)
    robot.oled.display_image(robot_view)


# Setup robot
robot = AlexRobot(
    motor_left_port="M3",
    motor_right_port="M0",
    ultrasonic_sensor_port="D1")


# On each camera frame, detect a line
robot.camera.on_frame = drive_based_on_frame


pause()
