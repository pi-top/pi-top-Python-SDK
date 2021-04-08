from pitop import Pitop, DriveController, PanTiltController, Camera
from pitop.labs import WebController
from helpers import calculate_velocity_twist, calculate_pan_tilt_angle

robot = Pitop()

robot.add_component(DriveController())
robot.add_component(PanTiltController())
robot.add_component(Camera())


def left_joystick(data):
    velocity_twist = calculate_velocity_twist(data)
    linear = velocity_twist.get('linear', 0)
    angular = velocity_twist.get('angular', 0)

    robot.drive.robot_move(linear, angular)


def right_joystick(data):
    angle = calculate_pan_tilt_angle(data)

    robot.pan_tilt.pan_servo.target_angle = angle.get('z')
    robot.pan_tilt.tilt_servo.target_angle = angle.get('y')


def reset(data):
    robot.drive.robot_move(0, 0)
    robot.pan_tilt.pan_servo.target_angle = 0
    robot.pan_tilt.tilt_servo.target_angle = 0


# This doesn't currently work as WebController hasn't been built as a component
robot.add_component(
    WebController(camera=robot.camera, handlers={
        'left_joystick': left_joystick,
        'right_joystick': right_joystick,
        'reset': reset
    })
)

robot.controller.serve_forever()
