from pitop import Pitop, alex_configuration

from random import randint
from time import sleep


# Load Alex configuration into a Pitop object
alex = Pitop.from_config(alex_configuration)

# Use miniscreen display
alex.miniscreen.display_multiline_text("hi!\nI'm Alex!")


def random_speed_factor():
    # 0.01 - 1, 0.01 resolution
    return randint(1, 100) / 100


def random_sleep():
    # 0.5 - 2, 0.5 resolution
    return randint(1, 4) / 2


# Move around randomly
alex.drive.forward(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.drive.left(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.drive.backward(speed_factor=random_speed_factor())
sleep(random_sleep())

alex.drive.right(speed_factor=random_speed_factor())
sleep(random_sleep())
