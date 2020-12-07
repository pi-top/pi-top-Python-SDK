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
        roll, pitch, yaw = self._imu_controller.orientation_data

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
        acc_data = self.accelerometer_raw
        x, y, z = itemgetter('x', 'y', 'z')(acc_data)
        roll = math.degrees(math.atan2(x, math.sqrt(y**2 + z**2)))
        pitch = math.degrees(math.atan2(-y, math.sqrt(x**2 + z**2)))

        data = {
            'roll': roll,
            'pitch': pitch
        }

        return data

    @property
    def accelerometer_raw(self):
        """
        Gets the raw x, y and z axis gyroscope data
        :return: A dictionary object indexed by the strings x, y and z. A dictionary object indexed by the strings x, y
            and z. The values are Floats representing the acceleration intensity of the axis in Gs.
        :rtype: dict
        """
        x, y, z = self._imu_controller.accelerometer_raw

        data = {
            'x': x,
            'y': y,
            'z': z
        }

        return data

    @property
    def gyroscope_raw(self):
        """
        Gets the raw x, y and z axis gyroscope data.
        :return: A dictionary object indexed by the strings x, y and z. A dictionary object indexed by the strings x, y
            and z. The values are Floats representing the rotational intensity of the axis in radians per second.
        :rtype: dict
        """
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
        Gets the raw x, y and z axis magnetometer data.
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
