from ptpma import PMAJoystick
from time import sleep

joystick = PMAJoystick("A0")

while True:
    print("x: {}, y: {}".format(joystick.value[0], joystick.value[1]))
    sleep(0.1)
