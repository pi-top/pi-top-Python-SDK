from pitop import AlexRobot

from random import randint
from time import sleep


# Set up Alex
alex = AlexRobot()

# Use miniscreen display
alex.miniscreen.display_multiline_text("hi!\nI'm Alex!")


def random_speed_factor():
    # 0.01 - 1, 0.01 resolution
    return randint(1, 100) / 100


def random_sleep():
    # 0.5 - 2, 0.5 resolution
    return randint(1, 4) / 2


# Move around randomly
alex.forward(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.left(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.backward(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.right(speed_factor=random_speed_factor())
sleep(random_sleep())
