#!/usr/bin/env python3

from pitop.pma.imu_controller import ImuController
import weakref
import math
import numpy as np
import threading
import time

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import proj3d


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

    def calibrate_magnetometer(self):
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


        with open('mag_data_3.npy', 'wb') as f:
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

        # x = self._mag_measurements[:, 0]
        # y = self._mag_measurements[:, 1]
        # z = self._mag_measurements[:, 2]
        # fig = plt.figure(figsize=(8, 8))
        # ax = fig.add_subplot(111, projection='3d')
        #
        # ax.scatter(x, y, z)
        # plt.show()

        return correction_vector, field_strength

    def poll_magnetometer_data(self, thread_event, imu_controller):
        print("Polling mag data...")
        prev_time = time.time()
        while not thread_event.is_set():
            current_time = time.time()
            if current_time - prev_time > (1 / self._MAG_POLL_FREQUENCY):
                x, y, z = imu_controller.magnetometer_raw
                new_mag_data = [x, y, z]
                self._mag_filter_array, mag_median = running_median(self._mag_filter_array, new_mag_data)
                self._mag_measurements = np.append(self._mag_measurements, [mag_median], axis=0)
                prev_time = current_time
            else:
                time.sleep(self._SLEEP_TIME)


class EllipsoidTool:
    """Some stuff for playing with ellipsoids"""

    def __init__(self):
        pass

    def getMinVolEllipse(self, P=None, tolerance=0.01):
        """ Find the minimum volume ellipsoid which holds all the points

        Based on work by Nima Moshtagh
        http://www.mathworks.com/matlabcentral/fileexchange/9542
        and also by looking at:
        http://cctbx.sourceforge.net/current/python/scitbx.math.minimum_covering_ellipsoid.html
        Which is based on the first reference anyway!

        Here, P is a numpy array of N dimensional points like this:
        P = [[x,y,z,...], <-- one point per line
             [x,y,z,...],
             [x,y,z,...]]

        Returns:
        (center, radii, rotation)

        """
        (N, d) = np.shape(P)
        d = float(d)

        # Q will be our working array
        Q = np.vstack([np.copy(P.T), np.ones(N)])
        QT = Q.T

        # initializations
        err = 1.0 + tolerance
        u = (1.0 / N) * np.ones(N)

        # Khachiyan Algorithm
        while err > tolerance:
            V = np.dot(Q, np.dot(np.diag(u), QT))
            M = np.diag(np.dot(QT, np.dot(np.linalg.inv(V), Q)))  # M the diagonal vector of an NxN matrix
            j = np.argmax(M)
            maximum = M[j]
            step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
            new_u = (1.0 - step_size) * u
            new_u[j] += step_size
            err = np.linalg.norm(new_u - u)
            u = new_u

        # center of the ellipse
        center = np.dot(P.T, u)

        # the A matrix for the ellipse
        print(np.dot(P.T, np.dot(np.diag(u), P)))
        print(np.array([[a * b for b in center] for a in center]))
        A = np.linalg.inv(
                            np.dot(P.T, np.dot(np.diag(u), P)) -
                            np.array([[a * b for b in center] for a in center])
                            ) / d
        print("A: {}".format(A))
        # G et the values we'd like to return
        U, s, rotation = np.linalg.svd(A)
        radii = 1.0 / np.sqrt(s)

        return center, radii, rotation, A

    def getEllipsoidVolume(self, radii):
        """Calculate the volume of the blob"""
        return 4. / 3. * np.pi * radii[0] * radii[1] * radii[2]

    def plotEllipsoid(self, center, radii, rotation, ax=None, plotAxes=False, cageColor='b', cageAlpha=0.2):
        """Plot an ellipsoid"""
        make_ax = ax is None
        if make_ax:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

        u = np.linspace(0.0, 2.0 * np.pi, 100)
        v = np.linspace(0.0, np.pi, 100)

        # cartesian coordinates that correspond to the spherical angles:
        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(np.ones_like(u), np.cos(v))
        # rotate accordingly
        for i in range(len(x)):
            for j in range(len(x)):
                [x[i, j], y[i, j], z[i, j]] = np.dot([x[i, j], y[i, j], z[i, j]], rotation) + center

        if plotAxes:
            # make some purdy axes
            axes = np.array([[radii[0], 0.0, 0.0],
                             [0.0, radii[1], 0.0],
                             [0.0, 0.0, radii[2]]])
            # rotate accordingly
            for i in range(len(axes)):
                axes[i] = np.dot(axes[i], rotation)

            # plot axes
            for p in axes:
                X3 = np.linspace(-p[0], p[0], 100) + center[0]
                Y3 = np.linspace(-p[1], p[1], 100) + center[1]
                Z3 = np.linspace(-p[2], p[2], 100) + center[2]
                ax.plot(X3, Y3, Z3, color=cageColor)

        # plot ellipsoid
        ax.plot_wireframe(x, y, z, rstride=4, cstride=4, color=cageColor, alpha=cageAlpha)

        if make_ax:
            plt.show()
            plt.close(fig)
            del fig


def apply_hard_iron_calibration(data):
    calibration_vector = [0.53196167, 36.61249794, 83.1567736]
    field = 41.740706425640774

    data_cal = data - calibration_vector

    # x_cal = (x_raw - calibration_vector[0])
    # y_cal = (y_raw - calibration_vector[1])
    # z_cal = (z_raw - calibration_vector[2])

    # return x_cal, y_cal, z_cal
    return data_cal


if __name__ == "__main__":
    # calibrator = ImuCalibration()
    # vector, field_strength = calibrator.calibrate_magnetometer()
    # print(vector)
    # print(field_strength)

    ellipsoid_tools = EllipsoidTool()

    with open('mag_data_3.npy', 'rb') as f:
        mag_data = np.load(f)

    normalized_mag_data = mag_data / 100.0

    x_uncal = normalized_mag_data[:, 0]
    y_uncal = normalized_mag_data[:, 1]
    z_uncal = normalized_mag_data[:, 2]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x_uncal, y_uncal, z_uncal)



    center, radii, rotation, A = ellipsoid_tools.getMinVolEllipse(P=normalized_mag_data)

    print(A)
    w_inverse = np.sqrt(A)

    print(w_inverse)

    ellipsoid_tools.plotEllipsoid(center, radii, rotation, ax=ax)

    rows, columns = np.shape(mag_data)
    # mag_data_cal = np.matmul(w_inverse, (normalized_mag_data - center).T)
    mag_data_cal = normalized_mag_data - center

    x_cal = mag_data_cal[:, 0]
    y_cal = mag_data_cal[:, 1]
    z_cal = mag_data_cal[:, 2]

    ax.scatter(x_cal, y_cal, z_cal, color='r')

    plt.show()


    # mag_data_cal = apply_hard_iron_calibration(mag_data)
    #
    # a_matrix, ellipsoid_center = get_ellipsoid_matrix(mag_data)
    # print(a_matrix)
    # print(ellipsoid_center)
    #
    # x_cal = mag_data_cal[:, 0]
    # y_cal = mag_data_cal[:, 1]
    # z_cal = mag_data_cal[:, 2]
    #
    # fig = plt.figure(figsize=(8, 8))
    # ax = fig.add_subplot(111, projection='3d')
    #
    # ax.scatter(x_uncal, y_uncal, z_uncal)
    # ax.scatter(x_cal, y_cal, z_cal)
    # plt.show()
