from pitop import Pitop, Camera, DriveController
# from pitop.processing.algorithms.line_detect import process_frame_for_line
# import cv2

from pitop.robotics.localization_2 import Localization

from signal import pause

from time import sleep

# Assemble a robot
robot = Pitop()
robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(Camera(0, (640, 480), rotate_angle=90, format='opencv'))

localization = Localization(robot)
localization.start()

robot_view = localization.robot_view

# cv2.imshow("Image", robot_view)
# cv2.waitKey(1)

# sleep(3)
# robot.drive.left(0.05, turn_radius=0.4)

# robot.drive.rotate(180, 3)

while True:
    robot.drive.forward(0.3)
    sleep(6)
    robot.drive.stop()
    sleep(1)
    robot.drive.rotate(180, 3)
    robot.drive.stop()
    sleep(1)



# angle = 0
#
# while angle < 180:
#     angle = localization.position.angle
#     print(f'angle: {angle:.2f}')
#     sleep(0.25)
#
# print('finished')

# pause()
