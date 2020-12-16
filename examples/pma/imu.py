from pitop.pma import Imu
from time import sleep
from dataclasses import fields

imu = Imu()

while True:
    acc = imu.accelerometer
    acc_x, acc_y, acc_z = list(getattr(acc, field.name) for field in fields(acc))
    gyro = imu.gyroscope
    gyro_x, gyro_y, gyro_z = list(getattr(gyro, field.name) for field in fields(gyro))
    mag = imu.magnetometer
    mag_x, mag_y, mag_z = list(getattr(mag, field.name) for field in fields(mag))

    orientation = imu.orientation
    roll, pitch, yaw = list(getattr(orientation, field.name) for field in fields(orientation))

    print("acc: {}, {}, {}".format(acc_x, acc_y, acc_z))
    print("gyro: {}, {}, {}".format(gyro_x, gyro_y, gyro_z))
    print("mag: {}, {}, {}".format(mag_x, mag_y, mag_z))
    print("orientation: {}, {}, {}".format(roll, pitch, yaw))
    sleep(0.1)
