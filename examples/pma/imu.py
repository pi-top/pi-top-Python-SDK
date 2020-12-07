from pitop.pma import Imu
from time import sleep

imu = Imu()

while True:
    acc = imu.accelerometer_raw
    gyro = imu.gyroscope_raw
    mag = imu.magnetometer_raw

    print("acc: {x}, {y}, {z}".format(**acc))
    print("gyro: {x}, {y}, {z}".format(**gyro))
    print("mag: {x}, {y}, {z}".format(**mag))
    sleep(0.1)
