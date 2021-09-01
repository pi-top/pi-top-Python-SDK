from signal import pause

from pitop import Camera, DriveController, Pitop
from pitop.processing.algorithms.line_detect import process_frame_for_line

# Assemble a robot
robot = Pitop()
robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(Camera())


# Set up logic based on line detection
def drive_based_on_frame(frame):
    processed_frame = process_frame_for_line(frame)

    if processed_frame.line_center is None:
        print("Line is lost!", end="\r")
        robot.drive.stop()
    else:
        print(f"Target angle: {processed_frame.angle:.2f} deg ", end="\r")
        robot.drive.forward(0.25, hold=True)
        robot.drive.target_lock_drive_angle(processed_frame.angle)
        robot.miniscreen.display_image(processed_frame.robot_view)


# On each camera frame, detect a line
robot.camera.on_frame = drive_based_on_frame


pause()
