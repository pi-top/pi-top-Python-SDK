#!/usr/bin/env python3

from .imu_controller import ImuController
import weakref

class Imu:
    def __init__(self):
        self._imu_controller = ImuController()
        weakref.finalize(self._imu_controller, self._imu_controller.cleanup)

    def get_orientation_radians(self):
        pass

    def get_orientation_degrees(self):
        pass

    def get_orientation(self):
        self.get_orientation_degrees()

    def get_acceleration(self):
        pass

    def get_accelerometer_raw(self):
        pass

    def get_gyroscope(self):
        pass

    def get_gyroscope_raw(self):
        pass

    def get_magnetometer(self):
        mag_data = self.get_magnetometer_raw()

        pass

    def get_magnetometer_raw(self):
        """
        Gets the raw x, y and z axis magnetometer data
        :return: A dictionary object indexed by the strings x, y and z. The values are Floats representing the magnetic
            intensity of the axis in microteslas (µT).
        :rtype: dict
        """
        pass

    def calibrate_gyroscope(self):
        pass

    def calibrate_magnetometer(self):
        pass



