#!/usr/bin/env python3

from .imu_controller import ImuController
import weakref
import math
from operator import itemgetter


class Imu:
    def __init__(self):
        self._imu_controller = ImuController()
        weakref.finalize(self._imu_controller, self._imu_controller.cleanup)

    @property
    def orientation_radians(self):
        data = self.orientation_degrees
        for key, value in data.items():
            data[key] = math.radians(value)
        return data

    @property
    def orientation_degrees(self):
        roll, pitch, yaw = self._imu_controller.orientation_data

        data = {
            'roll': roll,
            'pitch': pitch,
            'yaw': yaw
        }
        return data

    @property
    def orientation(self):
        return self.orientation_degrees

    @property
    def accelerometer_orientation(self):
        acc_data = self.accelerometer_raw
        x, y, z = itemgetter('x', 'y', 'z')(acc_data)
        roll = math.atan2(x, math.sqrt(y**2 + z**2)) * 180 / math.pi
        pitch = math.atan2(-y, math.sqrt(x**2 + z**2)) * 180 / math.pi

        data = {
            'roll': roll,
            'pitch': pitch
        }

        return data

    @property
    def accelerometer_raw(self):
        x, y, z = self._imu_controller.accelerometer_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def gyroscope_raw(self):
        x, y, z = self._imu_controller.gyroscope_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def magnetometer_raw(self):
        """
        Gets the raw x, y and z axis magnetometer data
        :return: A dictionary object indexed by the strings x, y and z. The values are Floats representing the magnetic
            intensity of the axis in microteslas (µT).
        :rtype: dict
        """
        x, y, z = self._imu_controller.magnetometer_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    def calibrate_gyroscope(self):
        pass

    def calibrate_magnetometer(self):
        pass
