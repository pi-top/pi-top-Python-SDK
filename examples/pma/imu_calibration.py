#!/usr/bin/env python3

from pitop.pma.imu_controller import ImuController
from pitop.pma.common.math_functions.ellipsoid_functions import least_squares_ellipsoid_fit, \
    get_ellipsoid_geometric_params, plot_ellipsoid
import weakref
import math
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
from scipy import linalg
from mpl_toolkits import mplot3d  # don't delete, actually required for "3d" plot type


def running_median(old_array, new_data):
    new_array = np.append(np.delete(old_array, 0, 0), [new_data], axis=0)
    new_median = np.median(new_array, axis=0)
    return new_array, new_median


class ImuCalibration:
    _MAG_POLL_FREQUENCY = 25.0  # Hz
    _GYRO_POLL_FREQUENCY = 5.0  # Hz
    _SLEEP_TIME = 0.005
    _MAG_DATA_TOLERANCE = 10.0
    _MAG_FILTER_SIZE = 5

    def __init__(self):
        self.imu_controller = ImuController()
        self.imu_controller.acc_enable = True
        self.imu_controller.gyro_enable = True
        self.imu_controller.mag_enable = True
        self._mag_measurements = np.zeros((1, 3), dtype=float)
        self._mag_filter_array = np.zeros((self._MAG_FILTER_SIZE, 3), dtype=float)
        weakref.finalize(self.imu_controller, self.imu_controller.cleanup)

    @property
    def mag_data(self):
        return self._mag_measurements

    def _rotation_check(self, axis: str):
        prev_time = time.time()
        degrees_rotated = 0
        while abs(degrees_rotated) < 360.0:
            current_time = time.time()
            dt = current_time - prev_time
            if dt > (1 / self._GYRO_POLL_FREQUENCY):
                x, y, z = self.imu_controller.gyroscope_raw
                if axis == 'x':
                    degrees_rotated += x * dt
                elif axis == 'y':
                    degrees_rotated += y * dt
                elif axis == 'z':
                    degrees_rotated += z * dt
                print("degrees_rotated: {}".format(degrees_rotated))
                prev_time = current_time
            else:
                time.sleep(self._SLEEP_TIME)

    def calibrate_magnetometer(self, test_data=None, save_data=False):
        if test_data is None:
            self._get_test_data()
        else:
            self._mag_measurements = test_data

        if save_data and test_data is None:
            print("Saving test data...")
            with open('mag_data_10.npy', 'wb') as f:
                np.save(f, self._mag_measurements[self._MAG_FILTER_SIZE:])

        print("Calculating calibration matrix...")

        field_strength = self.get_field_strength()

        M, n, d = self.get_ellipse_parameters()

        center, radii, rotation_matrix = get_ellipsoid_geometric_params(M, n, d)

        hard_iron_offset, soft_iron_matrix = self.get_calibration_matrices(M, n, d, field_strength)

        x_cal, y_cal, z_cal = self.calibrate_mag_data(field_strength, hard_iron_offset, soft_iron_matrix)

        self.plot_graphs(x_cal, y_cal, z_cal, center, radii, rotation_matrix, field_strength)

        return hard_iron_offset, soft_iron_matrix

    def _get_test_data(self):
        imu_controller = ImuController()
        thread_event = threading.Event()
        mag_poll_thread = threading.Thread(target=self._poll_magnetometer_data, args=[thread_event, imu_controller, ],
                                           daemon=True)
        mag_poll_thread.start()

        time.sleep(1)
        # thread_event.set()
        # mag_poll_thread.join()

        print("Rotate the pi-top [4] 360 degrees whilst the pi-top logo faces the ceiling.")
        self._rotation_check(axis='z')
        print("Done!")
        time.sleep(1)

        print("Turn the pi-top [4] so the pi-top logo is on it's side and faces the walls, then rotate 360 degrees.")
        self._rotation_check(axis='x')
        print("Done!")
        time.sleep(1)

        print("Turn the pi-top [4] so the pi-top logo faces you the right way up and rotation it 360 degrees")
        self._rotation_check(axis='y')
        print("Done!")

        thread_event.set()
        mag_poll_thread.join()

        time.sleep(1)

    def get_field_strength(self):
        # from  https://www.nxp.com/docs/en/application-note/AN4246.pdf
        squared_measurements = np.square(self._mag_measurements)

        matrix_y = np.sum(squared_measurements, axis=1)

        rows, columns = self._mag_measurements.shape
        ones = np.ones((rows, 1))
        matrix_x = np.column_stack((self._mag_measurements, ones))

        matrix_x_transpose = np.transpose(matrix_x)

        x_t_x_inverse = np.linalg.inv(np.matmul(matrix_x_transpose, matrix_x))
        x_t_y = np.matmul(matrix_x_transpose, matrix_y)

        beta_vector = np.matmul(x_t_x_inverse, x_t_y)

        correction_vector = 0.5 * beta_vector[0:3]

        field_strength = math.sqrt(beta_vector[3] + np.sum(np.square(correction_vector)))

        return field_strength

    def get_ellipse_parameters(self):
        x_uncal = self.mag_data[:, 0]
        y_uncal = self.mag_data[:, 1]
        z_uncal = self.mag_data[:, 2]

        M, n, d = least_squares_ellipsoid_fit(x_uncal, y_uncal, z_uncal)

        return M, n, d

    def get_calibration_matrices(self, M, n, d, field_strength):
        Minv = np.linalg.inv(M)

        soft_iron_matrix = np.real(field_strength / np.sqrt(np.dot(n.T, np.dot(Minv, n)) - d) * linalg.sqrtm(M))

        hard_iron_offset = -np.dot(Minv, n)

        return hard_iron_offset, soft_iron_matrix

    def calibrate_mag_data(self, field_strength, hard_iron_offset, soft_iron_matrix):
        x_uncal = self.mag_data[:, 0]
        y_uncal = self.mag_data[:, 1]
        z_uncal = self.mag_data[:, 2]
        x_cal = np.zeros(x_uncal.shape)
        y_cal = np.zeros(x_uncal.shape)
        z_cal = np.zeros(x_uncal.shape)

        error_sum = 0
        error_squared_sum = 0
        for i in range(len(x_uncal)):
            h_actual = np.array([[x_uncal[i], y_uncal[i], z_uncal[i]]]).T
            h_estimate = np.matmul(soft_iron_matrix, h_actual - hard_iron_offset)
            x_cal[i] = h_estimate[0]
            y_cal[i] = h_estimate[1]
            z_cal[i] = h_estimate[2]
            magnitude = np.sqrt(np.dot(h_estimate.T, h_estimate))
            error = (magnitude[0][0] - field_strength)
            error_squared = error ** 2
            error_sum += error
            error_squared_sum += error_squared
        print("Average Error: {}".format(error_sum / x_uncal.shape))
        print("Error Variance: {}".format(error_squared_sum / x_uncal.shape))

        return x_cal, y_cal, z_cal

    def plot_graphs(self, x_cal, y_cal, z_cal, center, radii, rotation_matrix, field_strength):
        x_uncal = self.mag_data[:, 0]
        y_uncal = self.mag_data[:, 1]
        z_uncal = self.mag_data[:, 2]

        fig1 = plt.figure(1, figsize=(10, 10), dpi=80)
        ax1 = fig1.add_subplot(111, projection='3d')
        ax1.axis('equal')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.scatter(x_uncal, y_uncal, z_uncal, s=5, color='r')

        plot_ellipsoid(center, radii, rotation_matrix, ax=ax1, plotAxes=True)

        fig2 = plt.figure(2, figsize=(10, 10), dpi=80)
        ax2 = fig2.add_subplot(111, projection='3d')
        ax2.axis('equal')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        ax2.scatter(x_cal, y_cal, z_cal, color='r')

        # # plot unit sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v)) * field_strength
        y = np.outer(np.sin(u), np.sin(v)) * field_strength
        z = np.outer(np.ones(np.size(u)), np.cos(v)) * field_strength
        ax2.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
        ax2.plot_surface(x, y, z, alpha=0.3, color='b')

        plt.show()

    def _poll_magnetometer_data(self, thread_event, imu_controller):
        print("Polling mag data...")
        prev_time = time.time()
        # error_tolerance = 0.01
        while not thread_event.is_set():
            current_time = time.time()
            if current_time - prev_time > (1 / self._MAG_POLL_FREQUENCY):
                x, y, z = imu_controller.magnetometer_raw
                # if abs(x) < error_tolerance and abs(y) < error_tolerance and abs(z) < error_tolerance:
                #     print("Read error, trying again...")
                #     continue
                new_mag_data = [x, y, z]
                self._mag_filter_array, mag_median = self._running_median(self._mag_filter_array, new_mag_data)
                self._mag_measurements = np.append(self._mag_measurements, [mag_median], axis=0)
                prev_time = current_time
            else:
                time.sleep(self._SLEEP_TIME)

    @staticmethod
    def _running_median(old_array, new_data):
        new_array = np.append(np.delete(old_array, 0, 0), [new_data], axis=0)
        new_median = np.median(new_array, axis=0)
        return new_array, new_median


if __name__ == "__main__":
    calibrator = ImuCalibration()
    with open('mag_data_4.npy', 'rb') as f:
        mag_data = np.load(f)
    hard_iron_offset, soft_iron_matrix = calibrator.calibrate_magnetometer(save_data=True)
    print("hard_iron_offset: {}".format(hard_iron_offset))
    print("soft_iron_matrix: {}".format(soft_iron_matrix))
    print(soft_iron_matrix)
