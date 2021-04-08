from pitop import DriveController, PanTiltController, Camera
from pitop.labs import WebController
from helpers import calculate_velocity_twist, calculate_pan_tilt_angle

drive = DriveController()
pan_tilt = PanTiltController()
camera = Camera()


def left_joystick(data):
    velocity_twist = calculate_velocity_twist(data)
    linear = velocity_twist.get('linear', 0)
    angular = velocity_twist.get('angular', 0)

    drive.robot_move(linear, angular)


def right_joystick(data):
    angle = calculate_pan_tilt_angle(data)

    pan_tilt.pan_servo.target_angle = angle.get('z')
    pan_tilt.tilt_servo.target_angle = angle.get('y')


def reset(data):
    drive.robot_move(0, 0)
    pan_tilt.pan_servo.target_angle = 0
    pan_tilt.tilt_servo.target_angle = 0


controller = WebController(camera=camera, handlers={
    'left_joystick': left_joystick,
    'right_joystick': right_joystick,
    'reset': reset
})

controller.serve_forever()
