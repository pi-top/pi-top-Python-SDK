from pitop import (
    Pitop,
    Camera,
    DriveController,
    PanTiltController
)
from pitop.labs import RobotDriveWebController
from pitop.processing.algorithms.line_detect import process_frame_for_line

# Assemble a robot
robot = Pitop()
robot.add_component(DriveController())
robot.add_component(PanTiltController())
robot.add_component(Camera())


# # Set up logic based on line detection
# def drive_based_on_frame(frame):
#     processed_frame = process_frame_for_line(frame)

#     if processed_frame.line_center is None:
#         print("Line is lost!", end="\r")
#         robot.drive.stop()
#     else:
#         print(f"Target angle: {processed_frame.angle:.2f} deg ", end="\r")
#         robot.drive.forward(0.25, hold=True)
#         robot.drive.target_lock_drive_angle(processed_frame.angle)
#         robot.miniscreen.display_image(processed_frame.robot_view)


# TODO: move to drive controller
MAX_LINEAR_SPEED = 0.44
MAX_ANGULAR_SPEED = 5.12

# TODO: get from pan-tilt/servo controller
# Does this account for zero point?
MAX_SERVO_ANGLE = 90

# Note: constants like this appear to be a bit of a mess...


def left_joystick(linear_speed_scale, angular_speed_scale):
    robot.drive.robot_move(
        linear_speed_scale * MAX_LINEAR_SPEED,
        angular_speed_scale * MAX_ANGULAR_SPEED
    )


def right_joystick(tilt_angle_scale, pan_angle_scale):
    robot.pan_tilt.pan_servo.target_angle = pan_angle_scale * MAX_SERVO_ANGLE
    robot.pan_tilt.tilt_servo.target_angle = tilt_angle_scale * MAX_SERVO_ANGLE


RobotDriveWebController(
    video_feed=lambda: process_frame_for_line(
        robot.camera.get_frame()
    ).robot_view,
    left_joystick=left_joystick,
    right_joystick=robot.pan_tilt.robot_move,
).serve_forever()
