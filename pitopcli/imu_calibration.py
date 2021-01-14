from pitop.pma.imu_controller import ImuController
from pitop.pma.common.math_functions.ellipsoid_functions import (
    least_squares_ellipsoid_fit,
    get_ellipsoid_geometric_params,
    plot_ellipsoid,
)

from math import (
    atan2,
    degrees,
    sqrt,
)
from os import path
from threading import (
    Event,
    Thread,
)
from time import (
    sleep,
    strftime,
    time,
)
from warnings import (
    catch_warnings,
    filterwarnings,
)


import atexit
import numpy as np
import matplotlib.pyplot as plt
# Enables "add_subplot(projection='3d')"
from mpl_toolkits import mplot3d  # noqa: F401
from scipy.linalg import sqrtm

from pitopcommon.logger import PTLogger


class ImuCalibration:
    __MAG_POLL_FREQUENCY = 25.0  # Hz
    __GYRO_POLL_FREQUENCY = 5.0  # Hz
    __SLEEP_TIME = 0.005
    __MAG_FILTER_SIZE = 5

    def __init__(self):
        self.imu_controller = ImuController()
        self.imu_controller.acc_enable = True
        self.imu_controller.gyro_enable = True
        self.imu_controller.mag_enable = True

        self.__mag_measurements = np.zeros((1, 3), dtype=float)
        self.__mag_filter_array = np.zeros((self.__MAG_FILTER_SIZE, 3), dtype=float)
        self.__hard_iron_offset = None
        self.__soft_iron_matrix = None
        self.__mag_measurements_calibrated = None
        self.__center = None
        self.__radii = None
        self.__rotation_matrix = None
        self.__field_strength = None
        self.__test_data = None
        self.__save_data_name = None
        atexit.register(self.imu_controller.cleanup)

    @property
    def mag_data(self):
        return self.__mag_measurements

    def calibrate_magnetometer(self, test_data=None, save_data_name=None, update_mcu=True):
        print("Starting magnetometer calibration")

        self.__test_data = test_data
        self.__save_data_name = save_data_name
        if test_data is None:
            self.__get_test_data()
        else:
            self.__mag_measurements = test_data

        if save_data_name and test_data is None:
            print("Saving test data...")
            with open(save_data_name, 'wb') as f:
                np.save(f, self.__mag_measurements[self.__MAG_FILTER_SIZE:])

        print("Calculating calibration parameters...")

        self.__field_strength = self.__get_field_strength()

        M, n, d = self.__get_ellipse_parameters()

        self.__center, self.__radii, self.__rotation_matrix = get_ellipsoid_geometric_params(M, n, d)

        self.__hard_iron_offset, self.__soft_iron_matrix = self.__get_calibration_matrices(M, n, d, self.__field_strength)

        print("_hard_iron_offset: {}".format(self.__hard_iron_offset))
        print("_soft_iron_matrix: {}".format(self.__soft_iron_matrix))

        self.__mag_measurements_calibrated = self.__calibrate_mag_data()

        if update_mcu:
            self.imu_controller.write_mag_cal_params(self.__hard_iron_offset, self.__soft_iron_matrix)

    def plot_graphs(self, path_to_save_figure="/tmp/"):
        if path_to_save_figure and not path.isdir(path_to_save_figure):
            print(f"Provided path {path_to_save_figure} is not a valid directory")
            return

        x_uncal = self.mag_data[:, 0]
        y_uncal = self.mag_data[:, 1]
        z_uncal = self.mag_data[:, 2]

        x_cal = self.__mag_measurements_calibrated[:, 0]
        y_cal = self.__mag_measurements_calibrated[:, 1]
        z_cal = self.__mag_measurements_calibrated[:, 2]

        fig1 = plt.figure(1, figsize=(10, 10), dpi=80)
        fig1.suptitle('Raw Magnetometer Data with Least Squares Ellipsoid Fit', fontsize=16)
        ax1 = fig1.add_subplot(111, projection='3d')
        ax1.axis('equal')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.scatter(x_uncal, y_uncal, z_uncal, color='r')
        plot_ellipsoid(self.__center, self.__radii, self.__rotation_matrix, ax=ax1, plotAxes=True)

        fig2 = plt.figure(2, figsize=(10, 10), dpi=80)
        fig2.suptitle('Calibrated Magnetometer Data with Field Strength Unit Sphere', fontsize=16)
        ax2 = fig2.add_subplot(111, projection='3d')
        ax2.axis('equal')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        ax2.scatter(x_cal, y_cal, z_cal, color='r')

        # # plot unit sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v)) * self.__field_strength
        y = np.outer(np.sin(u), np.sin(v)) * self.__field_strength
        z = np.outer(np.ones(np.size(u)), np.cos(v)) * self.__field_strength
        ax2.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
        ax2.plot_surface(x, y, z, alpha=0.3, color='b')

        path_to_file = path.join(path_to_save_figure, "magnetometer_calibration_" + strftime("%Y-%m-%d-%H-%M-%S") + ".png")
        plt.savefig(path_to_file)
        print(f"Calibration data was save to {path_to_file}")

    def __get_test_data(self):
        imu_controller = ImuController()
        thread_event = Event()
        mag_poll_thread = Thread(target=self.__poll_magnetometer_data, args=[thread_event, imu_controller, ],
                                 daemon=True)
        mag_poll_thread.start()

        sleep(1)

        print("Hold the pi-top flat in the air so roll and pitch angles are zero.")
        self.__orientation_check(axis='z')
        sleep(1)
        print("Now rotate the pi-top 360 degrees whilst keeping it flat.")
        self.__rotation_check(axis='z')
        print("Done!")
        sleep(1)

        print("Now turn the pi-top on it's side so the roll angle is +90 or -90 degrees.")
        self.__orientation_check(axis='x')
        sleep(1)
        print("Now rotate the pi-top 360 degrees whilst keeping it on its side.")
        self.__rotation_check(axis='x')
        print("Done!")
        sleep(1)

        print("Now turn the pi-top on it's other side so the pitch angle is +90 or -90 degrees.")
        self.__orientation_check(axis='y')
        sleep(1)
        print("Now rotate the pi-top 360 degrees whilst keeping it on its side.")
        self.__rotation_check(axis='y')
        print("Done!")
        sleep(1)

        print("Now rotate/spin the pi-top in as many directions as possible.")
        sleep(1)
        input("Press any key when finished")
        print("Done!")
        sleep(1)

        thread_event.set()
        mag_poll_thread.join()

        sleep(1)

    def __rotation_check(self, axis: str):
        prev_time = time()
        degrees_rotated = 0
        while abs(degrees_rotated) < 360.0:
            current_time = time()
            dt = current_time - prev_time
            if dt > (1 / self.__GYRO_POLL_FREQUENCY):
                x, y, z = self.imu_controller.gyroscope_raw
                if axis == 'x':
                    degrees_rotated += x * dt
                elif axis == 'y':
                    degrees_rotated += y * dt
                elif axis == 'z':
                    degrees_rotated += z * dt
                # print("degrees_rotated: {}".format(degrees_rotated))
                prev_time = current_time
            else:
                sleep(self.__SLEEP_TIME)

    def __orientation_check(self, axis: str):
        if axis not in ('x', 'y', 'z'):
            raise ValueError("axis value must me 'x', 'y' or 'z'.")

        def check_x_axis(roll_value, pitch_value):
            if abs(roll_value) > 85 and abs(pitch_value) < 5:
                print("---------- Correct orientation found ----------")
                return True

        def check_y_axis(roll_value, pitch_value):
            if abs(roll_value) < 5 and abs(pitch_value) > 85:
                print("---------- Correct orientation found ----------")
                return True

        def check_z_axis(roll_value, pitch_value):
            if abs(roll_value) < 5 and abs(pitch_value) < 5:
                print("---------- Correct orientation found ----------")
                return True

        if axis == 'x':
            roll_check = check_x_axis
        elif axis == 'y':
            roll_check = check_y_axis
        else:
            roll_check = check_z_axis

        while True:
            roll, pitch = self.accelerometer_orientation
            if roll_check(roll, pitch):
                break
            else:
                sleep(self.__SLEEP_TIME)

    def accelerometer_orientation(self):
        x, y, z = self.imu_controller.accelerometer_raw
        roll = degrees(atan2(x, sqrt(y ** 2 + z ** 2)))
        pitch = degrees(atan2(-y, sqrt(x ** 2 + z ** 2)))

        return roll, pitch

    def __poll_magnetometer_data(self, thread_event, imu_controller):
        print("Polling mag data...")
        sleep(1)
        prev_time = time()
        error_tolerance = 0.01
        error_count = 0
        while not thread_event.is_set():
            current_time = time()
            if current_time - prev_time > (1 / self.__MAG_POLL_FREQUENCY):
                x, y, z = imu_controller.magnetometer_raw
                if abs(x) < error_tolerance and abs(y) < error_tolerance and abs(z) < error_tolerance:
                    print("Read error, trying again...")
                    error_count += 1
                    if error_count > 50:
                        PTLogger.error("Cannot get magnetometer readings, please try re-docking your pi-top into the "
                                       "Expansion Plate and running the calibrator again.")
                        exit()
                    continue
                new_mag_data = [x, y, z]
                self.__mag_filter_array, mag_median = self.__running_median(self.__mag_filter_array, new_mag_data)
                self.__mag_measurements = np.append(self.__mag_measurements, [mag_median], axis=0)
                prev_time = current_time
            else:
                sleep(self.__SLEEP_TIME)

    @staticmethod
    def __running_median(old_array, new_data):
        new_array = np.append(np.delete(old_array, 0, 0), [new_data], axis=0)
        new_median = np.median(new_array, axis=0)
        return new_array, new_median

    def __get_field_strength(self):
        # from  https://www.nxp.com/docs/en/application-note/AN4246.pdf
        squared_measurements = np.square(self.__mag_measurements)

        matrix_y = np.sum(squared_measurements, axis=1)

        rows, columns = self.__mag_measurements.shape
        ones = np.ones((rows, 1))
        matrix_x = np.column_stack((self.__mag_measurements, ones))

        matrix_x_transpose = np.transpose(matrix_x)

        x_t_x_inverse = np.linalg.inv(np.matmul(matrix_x_transpose, matrix_x))
        x_t_y = np.matmul(matrix_x_transpose, matrix_y)

        beta_vector = np.matmul(x_t_x_inverse, x_t_y)

        correction_vector = 0.5 * beta_vector[0:3]

        field_strength = sqrt(beta_vector[3] + np.sum(np.square(correction_vector)))

        return field_strength

    def __get_ellipse_parameters(self):
        x_uncal = self.mag_data[:, 0]
        y_uncal = self.mag_data[:, 1]
        z_uncal = self.mag_data[:, 2]

        M, n, d = least_squares_ellipsoid_fit(x_uncal, y_uncal, z_uncal)

        return M, n, d

    def __get_calibration_matrices(self, M, n, d, field_strength):
        hard_iron_offset = None
        soft_iron_matrix = None

        with catch_warnings():
            filterwarnings('error')
            try:
                Minv = np.linalg.inv(M)
                soft_iron_matrix = np.real(field_strength / np.sqrt(np.dot(n.T, np.dot(Minv, n)) - d) * sqrtm(M))
                hard_iron_offset = -np.dot(Minv, n)
            except Warning as e:
                PTLogger.error("Calibration error: {}".format(e))
                if self.__test_data is None:
                    PTLogger.info("Starting calibration process again...")
                    sleep(3)
                    self.calibrate_magnetometer(test_data=self.__test_data, save_data_name=self.__save_data_name)
                else:
                    PTLogger.info("Please try again with different test data.")
                    exit()

        return hard_iron_offset, soft_iron_matrix

    def __calibrate_mag_data(self):
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
            h_estimate = np.matmul(self.__soft_iron_matrix, h_actual - self.__hard_iron_offset)
            x_cal[i] = h_estimate[0]
            y_cal[i] = h_estimate[1]
            z_cal[i] = h_estimate[2]
            magnitude = np.sqrt(np.dot(h_estimate.T, h_estimate))
            error = (magnitude[0][0] - self.__field_strength)
            error_squared = error ** 2
            error_sum += error
            error_squared_sum += error_squared
        print("Average Error: {}".format(error_sum / x_uncal.shape))
        print("Error Variance: {}".format(error_squared_sum / x_uncal.shape))

        mag_measurements_cal = np.hstack((np.array([x_cal]).T, np.array([y_cal]).T, np.array([z_cal]).T))

        return mag_measurements_cal
