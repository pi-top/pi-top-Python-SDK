#!/usr/bin/env python3

from .imu_controller import ImuController
import weakref
import math
from operator import itemgetter
# from .common import ImuCalibration


class Imu:
    def __init__(self):
        self.imu_controller = ImuController()
        self.imu_controller.acc_scaler = 2
        self.imu_controller.gyro_scaler = 250
        weakref.finalize(self.imu_controller, self.imu_controller.cleanup)

    @property
    def orientation_radians(self):
        """
        Gets the current orientation in radians using the aircraft principal axes of pitch, roll and yaw.
        :return: A dictionary object indexed by the strings pitch, roll and yaw. The values are Floats representing the
            angle of the axis in radians.
        :rtype: dict
        """
        data = self.orientation_degrees
        for key, value in data.items():
            data[key] = math.radians(value)
        return data

    @property
    def orientation_degrees(self):
        """
        Gets the current orientation in degrees using the aircraft principal axes of pitch, roll and yaw.
        :return: A dictionary object indexed by the strings pitch, roll and yaw. The values are Floats representing the
            angle of the axis in degrees.
        :rtype: dict
        """
        roll, pitch, yaw = self.imu_controller.orientation_data

        data = {
            'roll': roll,
            'pitch': pitch,
            'yaw': yaw
        }
        return data

    @property
    def orientation(self):
        """
        Calls orientation_degrees above.
        """
        return self.orientation_degrees

    @property
    def accelerometer_orientation(self):
        """
        Calculates roll and pitch orientations using only accelerometer data.
        :return: A dictionary object indexed by the strings pitch and roll. The values are Floats representing the angle
            of the axis in degrees.
        :rtype: dict
        """
        acc_data = self.accelerometer
        x, y, z = itemgetter('x', 'y', 'z')(acc_data)
        roll = math.degrees(math.atan2(x, math.sqrt(y**2 + z**2)))
        pitch = math.degrees(math.atan2(-y, math.sqrt(x**2 + z**2)))

        data = {
            'roll': roll,
            'pitch': pitch
        }

        return data

    @property
    def accelerometer(self):
        """
        Gets the x, y and z axis gyroscope data
        :return: A dictionary object indexed by the strings x, y and z. A dictionary object indexed by the strings x, y
            and z. The values are Floats representing the acceleration intensity of the axis in Gs.
        :rtype: dict
        """
        x, y, z = self.imu_controller.accelerometer_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def gyroscope(self):
        """
        Gets the x, y and z axis gyroscope data.
        :return: A dictionary object indexed by the strings x, y and z. A dictionary object indexed by the strings x, y
            and z. The values are Floats representing the rotational intensity of the axis in radians per second.
        :rtype: dict
        """
        x, y, z = self.imu_controller.gyroscope_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def magnetometer(self):
        """
        Gets the x, y and z axis magnetometer data.
        :return: A dictionary object indexed by the strings x, y and z. The values are Floats representing the magnetic
            intensity of the axis in microteslas (µT).
        :rtype: dict
        """
        x, y, z = self.imu_controller.magnetometer_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def acc_mag_orientation(self):
        """
        Calculates roll, pitch and yaw orientations using accelerometer and magnetometer data.
        :return: A dictionary object indexed by the strings roll, pitch and yaw. The values are Floats representing the
            angle of the axis in degrees.
        :rtype: dict
        """
        return

    def calibrate_magnetometer(self, hard_iron_offset, soft_iron_matrix):
        pass
