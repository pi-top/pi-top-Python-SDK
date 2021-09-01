from random import randint
from time import sleep

from pitop import Pitop
from pitop.robotics.drive_controller import DriveController

# Create a basic robot
robot = Pitop()
drive = DriveController(left_motor_port="M3", right_motor_port="M0")
robot.add_component(drive)


# Use miniscreen display
robot.miniscreen.display_multiline_text("hey there!")


def random_speed_factor():
    # 0.01 - 1, 0.01 resolution
    return randint(1, 100) / 100


def random_sleep():
    # 0.5 - 2, 0.5 resolution
    return randint(1, 4) / 2


# Move around randomly
robot.drive.forward(speed_factor=random_speed_factor())
sleep(random_sleep())

robot.drive.left(speed_factor=random_speed_factor())
sleep(random_sleep())

robot.drive.backward(speed_factor=random_speed_factor())
sleep(random_sleep())

robot.drive.right(speed_factor=random_speed_factor())
sleep(random_sleep())
