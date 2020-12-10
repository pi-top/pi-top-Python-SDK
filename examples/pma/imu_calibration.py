#!/usr/bin/env python3

from pitop.pma.imu_controller import ImuController
from pitop.pma.common.math_functions.ellipsoid import least_squares_ellipsoid_fit, get_ellipsoid_geometric_params, plot_ellipsoid
import weakref
import math
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
from scipy import linalg
from mpl_toolkits import mplot3d


def running_median(old_array, new_data):
    new_array = np.append(np.delete(old_array, 0, 0), [new_data], axis=0)
    new_median = np.median(new_array, axis=0)
    return new_array, new_median


class ImuCalibration:
    _MAG_POLL_FREQUENCY = 50.0  # Hz
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
        # print(self._mag_filter_array)
        weakref.finalize(self.imu_controller, self.imu_controller.cleanup)

    @property
    def mag_data(self):
        return self._mag_measurements

    def rotation_check(self, axis: str):
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

    def calibrate_magnetometer(self, save_data=False):
        imu_controller = ImuController()
        thread_event = threading.Event()
        mag_poll_thread = threading.Thread(target=self.poll_magnetometer_data, args=[thread_event, imu_controller, ],
                                           daemon=True)
        mag_poll_thread.start()

        time.sleep(1)
        # thread_event.set()
        # mag_poll_thread.join()

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

        thread_event.set()
        mag_poll_thread.join()

        time.sleep(1)

        if save_data:
            with open('mag_data_4.npy', 'wb') as f:
                np.save(f, self._mag_measurements[self._MAG_FILTER_SIZE:])

        print("Calculating calibration matrix...")

        # print("self._mag_measurements shape: {}".format(self._mag_measurements.shape))

        squared_measurements = np.square(self._mag_measurements)
        # print("squared_measurements shape: {}".format(squared_measurements.shape))

        matrix_y = np.sum(squared_measurements, axis=1)

        # print("matrix_y shape: {}".format(matrix_y.shape))

        rows, columns = self._mag_measurements.shape
        ones = np.ones((rows, 1))
        matrix_x = np.column_stack((self._mag_measurements, ones))
        # print("matrix_x shape: {}".format(matrix_x.shape))

        matrix_x_transpose = np.transpose(matrix_x)
        # print("matrix_x_transpose shape: {}".format(matrix_x_transpose.shape))

        x_t_x_inverse = np.linalg.inv(np.matmul(matrix_x_transpose, matrix_x))
        x_t_y = np.matmul(matrix_x_transpose, matrix_y)

        beta_vector = np.matmul(x_t_x_inverse, x_t_y)

        correction_vector = 0.5 * beta_vector[0:3]

        field_strength = math.sqrt(beta_vector[3] + np.sum(np.square(correction_vector)))

        return correction_vector, field_strength

    def poll_magnetometer_data(self, thread_event, imu_controller):
        print("Polling mag data...")
        prev_time = time.time()
        while not thread_event.is_set():
            current_time = time.time()
            if current_time - prev_time > (1 / self._MAG_POLL_FREQUENCY):
                x, y, z = imu_controller.magnetometer_raw
                new_mag_data = [x, y, z]
                self._mag_filter_array, mag_median = self.running_median(self._mag_filter_array, new_mag_data)
                self._mag_measurements = np.append(self._mag_measurements, [mag_median], axis=0)
                prev_time = current_time
            else:
                time.sleep(self._SLEEP_TIME)

    @staticmethod
    def running_median(old_array, new_data):
        new_array = np.append(np.delete(old_array, 0, 0), [new_data], axis=0)
        new_median = np.median(new_array, axis=0)
        return new_array, new_median


if __name__ == "__main__":
    # calibrator = ImuCalibration()
    # vector, field_strength = calibrator.calibrate_magnetometer(save_data=True)
    # print(vector)
    # print(field_strength)

    with open('mag_data_4.npy', 'rb') as f:
        mag_data = np.load(f)

    squared_measurements = np.square(mag_data)
    # print("squared_measurements shape: {}".format(squared_measurements.shape))

    matrix_y = np.sum(squared_measurements, axis=1)

    rows, columns = mag_data.shape
    ones = np.ones((rows, 1))
    matrix_x = np.column_stack((mag_data, ones))
    # print("matrix_x shape: {}".format(matrix_x.shape))

    matrix_x_transpose = np.transpose(matrix_x)
    # print("matrix_x_transpose shape: {}".format(matrix_x_transpose.shape))

    x_t_x_inverse = np.linalg.inv(np.matmul(matrix_x_transpose, matrix_x))
    x_t_y = np.matmul(matrix_x_transpose, matrix_y)

    beta_vector = np.matmul(x_t_x_inverse, x_t_y)

    correction_vector = 0.5 * beta_vector[0:3]

    field_strength = math.sqrt(beta_vector[3] + np.sum(np.square(correction_vector)))
    # mag_data = calibrator.mag_data

    x_uncal = mag_data[:, 0]
    y_uncal = mag_data[:, 1]
    z_uncal = mag_data[:, 2]

    # x_mean = np.mean(x_uncal)
    # y_mean = np.mean(y_uncal)
    # z_mean = np.mean(z_uncal)

    # x_uncal /= x_mean
    # y_uncal /= y_mean
    # z_uncal /= z_mean

    # center, radii, rotation, A = ellipsoid_tools.getMinVolEllipse(P=mag_data)

    M, n, d = least_squares_ellipsoid_fit(x_uncal, y_uncal, z_uncal)

    center, radii, rotation_matrix = get_ellipsoid_geometric_params(M, n, d)

    # a = M[0, 0]
    # b = M[1, 1]
    # c = M[2, 2]
    # f = M[2, 1]
    # g = M[0, 2]
    # h = M[0, 1]
    #
    # p = n[0][0]
    # q = n[1][0]
    # r = n[2][0]
    #
    # Q = np.array(
    #     [
    #         [a, h, g, p],
    #         [h, b, f, q],
    #         [g, f, c, r],
    #         [p, q, r, d]
    #     ]
    # )
    # print("Q: {}".format(Q))
    # print("M: {}".format(M))

    Minv = np.linalg.inv(M)
    # print(Qinv)

    # print(b)
    Ainv = np.real(field_strength / np.sqrt(np.dot(n.T, np.dot(Minv, n)) - d) * linalg.sqrtm(M))

    # Tofs = np.eye(4)
    # Tofs[3, 0:3] = center
    # # print("Tofs: {}".format(Tofs))
    # # print("np.dot(Q, Tofs.T): {}".format(np.dot(Q, Tofs.T)))
    # R = np.dot(Tofs, np.dot(Q, Tofs.T))
    # print("R: {}".format(R))

    # R3 = R[0:3, 0:3]
    # print(R3)
    # R3test = R3 / R3[0, 0]
    # print(R3test)
    # s1 = -R[3, 3]
    # R3S = R3 / s1
    # (el, ec) = np.linalg.eig(R3S)
    # rotation_matrix = np.linalg.inv(ec)  # inverse is actually the transpose here
    # print("rotation_matrix: {}".format(rotation_matrix))
    # recip = 1.0 / np.abs(el)
    # axes = np.sqrt(recip)
    # print("axes: {}".format(axes))




    # A = np.linalg.inv(Ainv)
    # print("A: {}".format(A))
    # U, s, rotation = np.linalg.svd(A)
    # radii = 1.0 / np.sqrt(s)
    # print("radii: {}".format(radii))
    #
    # center = b.T[0]
    # print("center: {}".format(center))

    # ellipsoid_tools.plotEllipsoid(center, radii, rotation, ax=ax1)

    # mag_data_cal = np.matmul((mag_data - d), Ainv) * field_strength

    calibratedX = np.zeros(x_uncal.shape)
    calibratedY = np.zeros(x_uncal.shape)
    calibratedZ = np.zeros(x_uncal.shape)

    b = -np.dot(Minv, n)

    totalError = 0
    for i in range(len(x_uncal)):
        h = np.array([[x_uncal[i], y_uncal[i], z_uncal[i]]]).T
        hHat = np.matmul(Ainv, h - b)
        calibratedX[i] = hHat[0]
        calibratedY[i] = hHat[1]
        calibratedZ[i] = hHat[2]
        mag = np.dot(hHat.T, hHat)
        err = (mag[0][0] - 1) ** 2
        totalError += err
    print("Total Error: %f" % totalError)

    # x_cal = mag_data_cal[:, 0]
    # y_cal = mag_data_cal[:, 1]
    # z_cal = mag_data_cal

    fig1 = plt.figure(1, figsize=(10, 10), dpi=80)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.scatter(x_uncal, y_uncal, z_uncal, s=5, color='r')

    plot_ellipsoid(center, radii, rotation_matrix, ax=ax1, plotAxes=True)

    fig2 = plt.figure(2, figsize=(10, 10), dpi=80)
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.scatter(calibratedX, calibratedY, calibratedZ, color='r')

    # # plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v)) * field_strength
    y = np.outer(np.sin(u), np.sin(v)) * field_strength
    z = np.outer(np.ones(np.size(u)), np.cos(v)) * field_strength
    ax2.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
    ax2.plot_surface(x, y, z, alpha=0.3, color='b')

    plt.show()
