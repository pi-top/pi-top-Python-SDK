from pitopcommon.logger import PTLogger

from .servo_controller import ServoController, ServoHardwareSpecs


class ServoMotor:
    """
    Represents a pi-top servo motor component.

    Note that pi-top servo motors use an open-loop control system. As such, the output of the device (e.g.
    the angle and speed of the servo horn) cannot be measured directly. This means that you can set a target
    angle or speed for the servo, but you cannot read the current angle or speed.

    :type port_name: str
    :param port_name:
        The ID for the port to which this component is connected.

    :type zero_point: int
    :param zero_point:
        A user-defined offset from 'true' zero.
    """

    def __init__(self, port, zero_point=0):
        self._controller = ServoController(port)

        self.min_angle = -ServoHardwareSpecs.ANGLE_RANGE / 2
        self.max_angle = ServoHardwareSpecs.ANGLE_RANGE / 2
        self.__has_set_angle = False
        self._zero_point = zero_point

    @property
    def zero_point(self):
        """
        Represents the servo motor angle that the library treats as 'zero'.
        This value can be anywhere in the range of -90 to +90.

        For example, if the zero_point were set to be -30, then the valid range
        of values for setting the angle would be -60 to +120.

        .. warning::
            Setting a zero point out of the range of -90 to 90 will cause the method
            to raise an exception.
        """

        return self._zero_point

    @zero_point.setter
    def zero_point(self, zero_position):
        hardware_min_angle = -ServoHardwareSpecs.ANGLE_RANGE / 2
        hardware_max_angle = ServoHardwareSpecs.ANGLE_RANGE / 2
        if not (hardware_min_angle <= zero_position <= hardware_max_angle):
            raise ValueError(f"Value must be from {hardware_min_angle} to {hardware_max_angle} degrees (inclusive)")

        self._zero_point = zero_position
        self.min_angle = hardware_min_angle - self._zero_point
        self.max_angle = hardware_max_angle - self._zero_point

    def get_angle_range(self):
        """
        Returns a tuple with minimum and maximum possible angles where the servo horn can be moved to.
        If :class:`zero_point` is set to 0 (default), the angle range will be (-90, 90).

        .. note::
            The maximum and minimum angles depend on the zero-point setting.
        """

        return (self.min_angle, self.max_angle)

    def get_target_angle(self):
        """
        Return the current angle of the servo motor horn.

        The value given is relative to the zero-point, which may either be true zero, or a user-set zero.
        The range of valid values is from -90 to +90 degrees, although in practice the servo will not support
        such a wide range of motion.

        .. warning::
            The method will return :data:`None` if called before using a method that moves the servo horn.
        """

        if not self.__has_set_angle:
            PTLogger.warning("The servo motor needs to perform a movement first in order to retrieve the target angle")
            return None

        target_angle = self._controller.get_target_angle()
        if target_angle is None:
            PTLogger.warning("No target_angle specified. Set one using set_target_angle()")
        return target_angle - self._zero_point

    def set_target_angle(self, angle, speed=50.0):
        """
        Sets the angle of the servo horn, relative to the zero position. Optionally, the speed at which
        the horn will move can also be provided.

        .. warning::
            Using an :data:`angle` out of the valid angle range will cause the method to raise an exception.
            To determine the valid angle range, use :class:`get_angle_range`.

        .. warning::
            Using a :data:`speed` out of the valid speed range will cause the method to raise an exception.

        :type angle: int or float
        :param angle:
            Set the angle of the servo motor horn; if using the default zero-point,
            ranges from -90 to +90 degrees.

        :type speed: int or float
        :param speed:
            Set the speed in deg/s as a positive number from 0 to 100. Defaults to 50.0.
        """

        if not (self.min_angle <= angle <= self.max_angle):
            raise ValueError(f"Angle value must be from {self.min_angle} to {self.max_angle} degrees (inclusive)")

        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")

        self._controller.set_target_angle(angle + self._zero_point, speed)
        self.__has_set_angle = True

    def get_target_speed(self):
        """
        Returns the speed at which the servo motor horn is set to move, from -100.0 to 100.0 deg/s.
        """

        target_speed = self._controller.get_target_speed()
        if target_speed is None:
            PTLogger.warning("No target_speed specified. Set it using set_target_speed()")
        return target_speed

    def set_target_speed(self, speed):
        """
        Move the servo horn from the current position to one of the servo motor limits (maximum/minimum possible angle),
        moving at the specified speed. The speed value must be a number from -100.0 to 100.0 deg/s.

        Setting a :data:`speed` value higher than zero will move the horn to the maximum angle (90 degrees by default),
        while a value less than zero will move it to the minimum angle (-90 degress by default).

        .. warning::
            Using a :data:`speed` out of the valid speed range will cause the method to raise an exception.

        :type speed: int or float
        :param speed:
            The target speed at which to move the servo horn, from -100 to 100 deg/s.
        """

        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")

        self._controller.set_target_speed(speed)
        self.__has_set_angle = True

    def set_acceleration_mode(self, mode):
        """
        Set the acceleration profile mode between default and smoothed. When setting the speed and/or position of the
        servos, this will determine how the Expansion Plate MCU will accelerate the servo's speed throughout an angle
        change.

        Default mode 0: speed will be constant throughout angle change
        Smoothed mode 1: servo speed will accelerate to the set speed at the start of movement and decelerate to 0 at
        the end of the movement.

        :type mode: int
        :param mode: value of 0 or 1 to choose default or smoothed mode
        """

        if mode not in (0, 1):
            raise ValueError("Mode value must be either 0 (default) or 1 (smoothed).")

        self._controller.set_acceleration_mode(mode)
