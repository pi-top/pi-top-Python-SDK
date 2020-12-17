from .imu_controller import ImuController
import math
from dataclasses import astuple, dataclass, fields
from abc import ABC
import atexit


@dataclass
class BaseDataType(ABC):

    def __add__(self, other):
        return self.__class__(*(getattr(self, dim.name) + getattr(other, dim.name) for dim in fields(self)))

    def __sub__(self, other):
        return self.__class__(*(getattr(self, dim.name) - getattr(other, dim.name) for dim in fields(self)))

    def __mul__(self, other):
        return self.__class__(*(getattr(self, dim.name) * other for dim in fields(self)))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Vector3D(BaseDataType):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Orientation(BaseDataType):
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


class IMU:
    def __init__(self):
        self.imu_controller = ImuController()
        self.imu_controller.acc_scaler = 2
        self.imu_controller.gyro_scaler = 250
        atexit.register(self.imu_controller.cleanup)

    @property
    def orientation_radians(self):
        """
        Gets the current orientation in radians using the aircraft principal axes of pitch, roll and yaw.
        :return: A :class:`Orientation` object with attributes of pitch, roll and yaw. The values are Floats
        representing the angle of the axis in radians.
        :rtype: Orientation()
        """
        orientation_degrees = self.orientation_degrees
        orientation_radians = orientation_degrees * math.pi / 180.0

        return orientation_radians

    @property
    def orientation_degrees(self):
        """
        Gets the current orientation in degrees using the aircraft principal axes of pitch, roll and yaw.
        :return: A :class:`Orientation` object with attributes of pitch, roll and yaw. The values are Floats
        representing the angle of the axis in degrees.
        :rtype: Orientation()
        """
        roll, pitch, yaw = self.imu_controller.orientation_data

        orientation = Orientation()
        orientation.roll = roll
        orientation.pitch = pitch
        orientation.yaw = yaw

        return orientation

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
        :return: A :class:`Orientation` object with attributes of pitch, roll and yaw. The values are Floats
                representing the angle of the axis in degrees. Yaw is always zero for this method.
        :rtype: Orientation()
        """
        acc_data = self.accelerometer
        x, y, z = list(getattr(acc_data, field.name) for field in fields(acc_data))
        roll = -math.degrees(math.atan2(x, math.sqrt(y ** 2 + z ** 2)))
        pitch = -math.degrees(math.atan2(-y, math.sqrt(x ** 2 + z ** 2)))

        orientation = Orientation()
        orientation.roll = roll
        orientation.pitch = pitch

        return orientation

    @property
    def accelerometer(self):
        """
        Gets the x, y and z axis accelerometer data.
        :return: A :class:`Vector3D` object with attributes x, y and z. The values are Floats representing the
                acceleration intensity of the axis in Gs.
        :rtype: Vector3D()
        """
        x, y, z = self.imu_controller.accelerometer_raw

        acc_vector = Vector3D()
        acc_vector.x = x
        acc_vector.y = y
        acc_vector.z = z

        return acc_vector

    @property
    def gyroscope(self):
        """
        Gets the x, y and z axis gyroscope data.
        :return: A :class:`Vector3D` object with attributes x, y and z. The values are Floats representing the
                rotational intensity of the axis in degrees per second.
        :rtype: Vector3D()
        """
        x, y, z = self.imu_controller.gyroscope_raw

        gyro_vector = Vector3D()
        gyro_vector.x = x
        gyro_vector.y = y
        gyro_vector.z = z

        return gyro_vector

    @property
    def magnetometer(self):
        """
        Gets the x, y and z axis magnetometer data.
        :return: A :class:`Vector3D` object with attributes x, y and z. The values are Floats representing the magnetic
            intensity of the axis in microteslas (µT).
        :rtype: Vector3D()
        """
        # TODO: calibrate data here based on programmed values in MCU, or create MCU register to set if we want
        #  calibrated or uncalibrated data returned
        x, y, z = self.imu_controller.magnetometer_raw

        mag_vector = Vector3D()
        mag_vector.x = x
        mag_vector.y = y
        mag_vector.z = z

        return mag_vector
