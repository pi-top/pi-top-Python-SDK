from pitop import Pitop, Camera, DriveController
from pitop.processing.algorithms.line_detect import process_frame_for_line

from pitop.robotics.localization_2 import Localization

from signal import pause

from time import sleep

# Assemble a robot
robot = Pitop()
robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(Camera())

localization = Localization(camera=robot.camera, drive_controller=robot.drive)

localization.track_position()


robot.drive.left(0.1, turn_radius=0.1)

angle = 0

while angle < 180:
    angle = localization.position.angle
    print(f'angle: {angle:.2f}')
    sleep(0.25)

print('finished')