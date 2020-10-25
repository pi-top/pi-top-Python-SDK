from .plate_interface import PlateInterface


class PMAInertialMeasurementUnit:
    """
    Functions for the Expansion Plate's built-in Inertial Measurement Unit (IMU)
    The IMU features an accelerometer, magnetometer and gyroscope. For advanced users,
    it is also possible to adjust the range of these measurements, to maximise the
    resolution for any given application.
    """

    # --------------------------------------------------------------------------------------------------------#
    def __init__(self):
        self._imu_device = PlateInterface.instance().get_device_imu()

    # --------------------------------------------------------------------------------------------------------#
    def calibrate(self):
        """
        Calibration for the magitometer. Follow the on screen instructions when called.
        """

        self._imu_device.run_interactive_calibration()

    # --------------------------------------------------------------------------------------------------------#

    @property
    def acceleration(self):
        """
        The current readings from the IMU's Accelerometer.
        An accelerometer is an electromechanical device used to measure acceleration forces.
        Such forces may be static, like the continuous force of gravity or, as is the case with many mobile devices,
        dynamic to sense movement or vibrations.

        :return: Accelerometer X, Y, Z axis values in m/s^2, as a 3-tuple
        :rtype: tuple
        """

        return self._imu_device.read_acceleration()

    # --------------------------------------------------------------------------------------------------------#
    @property
    def gyro(self):
        """
        The current readings from the IMU's Gyroscope.
        Gyroscopes, or gyros, are devices that measure or maintain rotational motion.
        MEMS (microelectromechanical system) gyros are small, inexpensive sensors that measure angular velocity.

        :return: Gyroscope X, Y, Z axis values in degrees/second, as a 3-tuple
        :rtype: tuple
        """

        return self._imu_device.read_gyroscope()

    # --------------------------------------------------------------------------------------------------------#
    @property
    def magnetic(self):
        """
        The current readings from the IMU's Magnetometer.
        A magnetometer is a device that measures magnetism—the direction, strength, or relative change of a magnetic field at a particular location.
        A compass is one such device, one that measures the direction of an ambient magnetic field, in this case, the Earth's magnetic field.

        :return: Magnetometer X, Y, Z axis values in gauss units, as a 3-tuple
        :rtype: tuple
        """

        return self._imu_device.read_magnetometer()

    # --------------------------------------------------------------------------------------------------------#
    @property
    def temperature(self):
        """
        The current temperature reading of the IMU's Thermometer.
        A thermometer is a device that measures temperature.

        :return: Internal temperature of the IMU in degrees Celsius.
        :rtype: float
        """

        return self._imu_device.read_temperature()

    # --------------------------------------------------------------------------------------------------------#
    @property
    def heading(self):
        """
        The direction heading(calibrated 0th degrees, north by default) of the IMU.
        Using the magnetometer we calculate which way is north with or without an offset.

        :return: direction heading of the IMU in 360 degrees.
        :rtype: float
        """

        return self._imu_device.mag_heading()

    # --------------------------------------------------------------------------------------------------------#
    @property
    def orientation(self):
        """
        The current orientation of the IMU.
        This uses the Madgwick algorithm with the acceleration, gyroscope and magnetometer we are able to
        calculate the orientation of device.

        :return: Orientation roll, pitch, yaw values as a 3-tuple
        :rtype: tuple
        """

        return self._imu_device.read_orientation()

    # --------------------------------------------------------------------------------------------------------#
