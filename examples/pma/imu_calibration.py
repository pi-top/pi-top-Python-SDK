#!/usr/bin/env python3

from pitop.pma.imu_controller import ImuController
import weakref
import math
import numpy as np
import threading
import time


class ImuCalibration:
    _POLL_FREQUENCY = 10.0  # Hz
    _SLEEP_TIME = 0.005

    def __init__(self):
        self.imu_controller = ImuController()
        self._thread_event = None
        self._mag_measurements = np.zeros((1, 3), dtype=int)
        weakref.finalize(self.imu_controller, self.imu_controller.cleanup)

    def rotation_check(self, axis: str):
        prev_time = time.time()
        degrees_rotated = 0
        while degrees_rotated < 360:
            current_time = time.time()
            dt = current_time - prev_time
            if dt > (1 / self._POLL_FREQUENCY):
                x, y, z = self.imu_controller.gyroscope_raw
                if axis == 'x':
                    degrees_rotated += x * dt
                elif axis == 'y':
                    degrees_rotated += y * dt
                elif axis == 'z':
                    degrees_rotated += z * dt
            else:
                time.sleep(self._SLEEP_TIME)

    def calibrate_magnetometer(self):
        self._thread_event = threading.Event()
        mag_poll_thread = threading.Thread(target=self.poll_magnetometer_data())
        mag_poll_thread.start()

        print("Rotate the pi-top [4] 360 degrees whilst the pi-top logo faces the ceiling.")
        self.rotation_check(axis='z')
        print("Done!")
        time.sleep(1)

        print("Turn the pi-top [4] so the pi-top logo is on it's side and faces the walls, then rotate 360 degrees.")
        self.rotation_check(axis='x')
        print("Done!")
        time.sleep(1)

        print("Turn the pi-top [4] so the pi-top logo faces you the right way up and rotation it 360 degrees")
        self.rotation_check(axis='y')
        print("Done!")
        time.sleep(1)

        print("Calculating calibration matrix...")

        squared_measurements = np.square(self._mag_measurements)

        matrix_y = np.sum(squared_measurements, axis=1)

        rows, columns = self._mag_measurements.shape
        ones = np.ones((rows, 1))
        matrix_x = np.column_stack((self._mag_measurements, ones))

        matrix_x_transpose = np.transpose(matrix_x)

        x_t_x_inverse = np.linalg.inv(np.matmul(matrix_x_transpose, matrix_x))
        x_t_y = np.matmul(matrix_x_transpose, matrix_y)

        beta_vector = np.matmul(x_t_x_inverse, x_t_y)

        correction_vector = 0.5 * beta_vector

        return correction_vector

    def poll_magnetometer_data(self):
        prev_time = time.time()
        while not self._thread_event.is_set():
            current_time = time.time()
            if current_time - prev_time > (1 / self._POLL_FREQUENCY):
                x, y, z = self.imu_controller.magnetometer_raw
                np.append(self._mag_measurements, [x, y, z])
                prev_time = current_time
            else:
                time.sleep(self._SLEEP_TIME)
