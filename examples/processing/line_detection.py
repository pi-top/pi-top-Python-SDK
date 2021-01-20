from pitop import RoverAlex
from pitop.processing.algorithms.line_detect import (
    find_line,
    get_control_angle,
)

from signal import pause


# Set up logic based on line detection
def drive_based_on_frame(frame):
    centroid, robot_view = find_line(frame)
    angle = get_control_angle(centroid, robot_view)
    print(f"Target angle: {angle:.2f} ", end="\r")
    rover.left(1)
    rover.oled.draw_image(robot_view)


rover = RoverAlex(motor_left_port="M3", motor_right_port="M0")
rover.camera.on_new_frame = drive_based_on_frame


pause()
