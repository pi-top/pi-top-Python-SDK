import time
from pitop.pma import Imu


imu = Imu()
prev_time = time.time()
degrees_rotated = 0
while abs(degrees_rotated) < 360.0:
    current_time = time.time()
    dt = current_time - prev_time
    if dt > (1 / 10.0):
        # x, y, z = self.imu_controller.gyroscope_raw
        gyro = imu.gyroscope
        print("gyro: {x}, {y}, {z}".format(**gyro))
        # if axis == 'x':
        #     degrees_rotated += x * dt
        # elif axis == 'y':
        #     degrees_rotated += y * dt
        # elif axis == 'z':
        #     degrees_rotated += z * dt
        prev_time = current_time
    else:
        time.sleep(0.01)