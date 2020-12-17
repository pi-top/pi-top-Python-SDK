from pitop.pma import Joystick
from time import sleep

joystick = Joystick("A0")

while True:
    print(f"x: {joystick.value[0]}, y: {joystick.value[1]}")
    sleep(0.1)
