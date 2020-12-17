from pitopcommon.logger import PTLogger
import atexit
from .servo_controller import ServoController, ServoHardwareSpecs
from dataclasses import dataclass


@dataclass
class ServoMotorState:
    angle: float = 0.0
    speed: float = 0.0


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
    _DEFAULT_SPEED = 50.0

    def __init__(self, port, zero_point=0):
        self._controller = ServoController(port)
        self._target_state = ServoMotorState()
        self._min_angle = self._HARDWARE_MIN_ANGLE
        self._max_angle = self._HARDWARE_MAX_ANGLE
        self.__has_set_angle = False
        self._zero_point = zero_point
        atexit.register(self._controller.cleanup)

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
    def state(self):
        """
        Returns the current state of the servo motor, giving curent angle and current speed.
        :return: :class:'ServoMotorState` object that has angle and speed attributes.
        """
        if not self.__has_set_angle:
            PTLogger.warning("The servo motor needs to perform a movement first in order to retrieve angle or speed.")
            return None, None

        angle, speed = self._controller.get_current_angle_and_speed()
        current_state = ServoMotorState()
        current_state.angle = angle
        current_state.speed = speed
        return current_state

    @state.setter
    def state(self, target_state: ServoMotorState):
        """
        Sets the target state of the servo horn, relative to the zero position.

        .. warning::
            Using an :data:`target_state.angle` out of the valid angle range will cause the method to raise an
            exception. To determine the valid angle range, use :meth:`ServoMotor.get_angle_range`.

        .. warning::
            Using a :data:`target_state.speed` out of the valid speed range will cause the method to raise an exception.

        :type target_state: :class:`ServoMotorState`
        :param target_state:
            Set the target servo state using the :class:`ServoMotorState` class, both :meth:`ServoMotorState.speed` and
            :meth:`ServoMotorState.angle` must be passed. Example usage:

            .. code-block:: python
                from pitop.pma import ServoMotor, ServoMotorState
                servo = ServoMotor()
                target_state = ServoMotorState()
                target_state.angle = 45
                target_state.speed = 20
                servo.state = target_state

        """
        angle = target_state.angle
        speed = target_state.speed

        if not (self._min_angle <= angle <= self._max_angle):
            raise ValueError(f"Angle value must be from {self._min_angle} to {self._max_angle} degrees (inclusive)")
        else:
            self._target_state.angle = angle

        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")
        else:
            self._target_state.speed = speed

        self._controller.set_target_angle(angle + self._zero_point, speed)
        self.__has_set_angle = True

    @property
    def current_angle(self):
        """
        Returns the current angle that the servo motor is at.
        :return: float value of the current angle of the servo motor in degrees.
        .. note::
        If you need synchronized angle and speed values, use :meth:`ServoMotor.state` instead, this will return both
        current angle and current speed at the same time.
        """
        return self.state.angle

    @property
    def current_speed(self):
        """
        Returns the current speed the servo motor is at.
        :return: float value of the current speed of the servo motor in deg/s.
        .. note::
        If you need synchronized angle and speed values, use :meth:`ServoMotor.state` instead, this will return both
        current angle and current speed at the same time.
        """
        return self.state.speed

    @property
    def target_angle(self):
        """
        Returns the last target angle that has been set.
        :return: float value of the target angle of the servo motor in deg.
        """
        if not self.__has_set_angle:
            PTLogger.warning("You should initialise the servo motor with an angle first, e.g. using .target_angle = 0")
        return self._target_state.angle

    @target_angle.setter
    def target_angle(self, angle):
        """
        Set the target angle you want the servo motor to go to
        :type angle: float
        :param angle: target servo motor angle.
        """
        target_state = ServoMotorState()
        target_state.angle = angle
        target_state.speed = self._DEFAULT_SPEED
        self.state = target_state

    @property
    def target_speed(self):
        """
        Returns the last target speed that has been set.
        :return: float value of the target speed of the servo motor in deg/s.
        """
        return self._target_state.speed

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
            PTLogger.warning("You should initialise the servo motor with an angle first, e.g. using .target_angle = 0")

        angle_setting = self._min_angle if speed < 0 else self._max_angle

        target_state = ServoMotorState()
        target_state.angle = angle_setting
        target_state.speed = speed

        self.state = target_state
