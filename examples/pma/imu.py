from pitop.pma import Imu
from time import sleep

imu = Imu()

while True:
    acc = imu.accelerometer
    gyro = imu.gyroscope
    mag = imu.magnetometer

    print("acc: {x}, {y}, {z}".format(**acc))
    print("gyro: {x}, {y}, {z}".format(**gyro))
    print("mag: {x}, {y}, {z}".format(**mag))
    sleep(0.1)
