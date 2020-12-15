from pitopcommon.logger import PTLogger
import weakref

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
    _HARDWARE_MIN_ANGLE = -ServoHardwareSpecs.ANGLE_RANGE / 2
    _HARDWARE_MAX_ANGLE = ServoHardwareSpecs.ANGLE_RANGE / 2

    def __init__(self, port, zero_point=0):
        self._controller = ServoController(port)
        self._min_angle = self._HARDWARE_MIN_ANGLE
        self._max_angle = self._HARDWARE_MAX_ANGLE
        self.__has_set_angle = False
        self._zero_point = zero_point
        self._target_speed = 0
        self._target_angle = 0
        weakref.finalize(self._controller, self._controller.cleanup)

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
        if not (self._HARDWARE_MIN_ANGLE <= zero_position <= self._HARDWARE_MAX_ANGLE):
            raise ValueError(f"Value must be from {self._HARDWARE_MIN_ANGLE} to {self._HARDWARE_MAX_ANGLE} degrees "
                             f"(inclusive)")

        self._zero_point = zero_position
        self._min_angle = self._HARDWARE_MIN_ANGLE - self._zero_point
        self._max_angle = self._HARDWARE_MAX_ANGLE - self._zero_point

    @property
    def angle_range(self):
        """
        Returns a tuple with minimum and maximum possible angles where the servo horn can be moved to.
        If :class:`zero_point` is set to 0 (default), the angle range will be (-90, 90).

        .. note::
            The maximum and minimum angles depend on the zero-point setting.
        """

        return self._min_angle, self._max_angle

    @property
    def current_angle_and_speed(self):
        if not self.__has_set_angle:
            PTLogger.warning("The servo motor needs to perform a movement first in order to retrieve angle or speed.")
            return None, None

        angle, speed = self._controller.get_current_angle_and_speed()
        return angle, speed

    @property
    def current_angle(self):
        return self.current_angle_and_speed[0]

    @property
    def current_speed(self):
        return self.current_angle_and_speed[1]

    def set_target_angle_and_speed(self, angle, speed=50.0):
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

        if not (self._min_angle <= angle <= self._max_angle):
            raise ValueError(f"Angle value must be from {self._min_angle} to {self._max_angle} degrees (inclusive)")
        else:
            self._target_angle = angle

        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")
        else:
            self._target_speed = speed

        self._controller.set_target_angle(angle + self._zero_point, speed)
        self.__has_set_angle = True

    @property
    def target_angle(self):
        return self._target_angle

    @target_angle.setter
    def target_angle(self, angle):
        self.set_target_angle_and_speed(angle)

    @property
    def target_speed(self):
        return self._target_speed

    @target_speed.setter
    def target_speed(self, speed):
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
        if not self.__has_set_angle:
            PTLogger.warning("You should initialise the servo motor with an angle first, e.g. using set_target_angle(0)")

        angle_setting = self._min_angle if speed < 0 else self._max_angle

        self.set_target_angle_and_speed(angle_setting, speed)
