from ptpma import PMAInertialMeasurementUnit
from time import sleep

imu = PMAInertialMeasurementUnit()

last_direction = ""
direction = ""

while True:
    roll, pitch, yaw = imu.orientation

    if(yaw > 337.5 or 22.5 > yaw):
        direction = "Heading north"
    elif(67.5 > yaw > 22.5):
        direction = "Heading north-east"
    elif(112.5 > yaw > 67.5):
        direction = "Heading east"
    elif(157.5 > yaw > 112.5):
        direction = "Heading south-east"
    elif(202.5 > yaw > 157.5):
        direction = "Heading south"
    elif(247.5 > yaw > 202.5):
        direction = "Heading south-west"
    elif(292.5 > yaw > 247.5):
        direction = "Heading west"
    elif(337.5 > yaw > 292.5):
        direction = "Heading north-west"

    if direction != last_direction:
        print(direction)
        last_direction = direction

    sleep(0.1)
