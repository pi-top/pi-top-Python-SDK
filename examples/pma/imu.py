from pitop.pma import IMU
from time import sleep
from dataclasses import fields

imu = IMU()

while True:
    acc = imu.accelerometer
    acc_x, acc_y, acc_z = list(getattr(acc, field.name) for field in fields(acc))
    gyro = imu.gyroscope
    gyro_x, gyro_y, gyro_z = list(getattr(gyro, field.name) for field in fields(gyro))
    mag = imu.magnetometer
    mag_x, mag_y, mag_z = list(getattr(mag, field.name) for field in fields(mag))

    orientation_fusion = imu.orientation
    roll, pitch, yaw = list(getattr(orientation_fusion, field.name) for field in fields(orientation_fusion))

    orientation_accelerometer = imu.accelerometer_orientation
    roll_acc, pitch_acc, _ = list(getattr(orientation_accelerometer, field.name) for field in fields(orientation_accelerometer))

    print(f"acc: {acc_x}, {acc_y}, {acc_z}")
    print(f"gyro: {gyro_x}, {gyro_y}, {gyro_z}")
    print(f"mag: {mag_x}, {mag_y}, {mag_z}")
    print(f"orientation_fusion: {roll}, {pitch}, {yaw}")
    print(f"orientation_accelerometer: {roll_acc}, {pitch_acc}")
    sleep(0.1)
