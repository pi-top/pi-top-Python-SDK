from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma.servo_controller import (
    ServoController,
    ServoHardwareSpecs,
)

# import atexit
from dataclasses import dataclass


@dataclass
class ServoMotorSetting:
    angle: float = 0.0
    speed: float = 0.0


class ServoMotor(Stateful, Recreatable):
    """Represents a pi-top servo motor component.

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
    __HARDWARE_MIN_ANGLE = -ServoHardwareSpecs.ANGLE_RANGE / 2
    __HARDWARE_MAX_ANGLE = ServoHardwareSpecs.ANGLE_RANGE / 2
    __DEFAULT_SPEED = 50.0

    def __init__(self, port_name, zero_point=0, name="servo"):
        self._pma_port = port_name
        self.name = name

        self.__controller = ServoController(self._pma_port)

        self.__target_state = ServoMotorSetting()
        self.__target_angle = 0.0
        self.__target_speed = self.__DEFAULT_SPEED

        self.__min_angle = self.__HARDWARE_MIN_ANGLE
        self.__max_angle = self.__HARDWARE_MAX_ANGLE
        self.__has_set_angle = False
        self.__zero_point = zero_point
        # TODO: re-add cleanup when firmware 'current_speed' bug is resolved
        # This bug is causing cleanup to be called every time, even if servo is not moving
        #
        # atexit.register(self.__cleanup)

        Stateful.__init__(self)
        Recreatable.__init__(self, config_dict={"port_name": port_name, "name": name, "zero_point": lambda: self.zero_point})

    @property
    def own_state(self):
        return {
            'angle': self.current_angle,
            'speed': self.current_speed,
        }

    def __cleanup(self):
        if self.__has_set_angle and self.current_speed != 0.0:
            self.__controller.cleanup()

    @property
    def zero_point(self):
        """Represents the servo motor angle that the library treats as 'zero'.
        This value can be anywhere in the range of -90 to +90.

        For example, if the zero_point were set to be -30, then the valid range
        of values for setting the angle would be -60 to +120.

        .. warning::
            Setting a zero point out of the range of -90 to 90 will cause the method
            to raise an exception.
        """

        return self.__zero_point

    @zero_point.setter
    def zero_point(self, zero_position):
        if not (self.__HARDWARE_MIN_ANGLE <= zero_position <= self.__HARDWARE_MAX_ANGLE):
            raise ValueError(f"Value must be from {self.__HARDWARE_MIN_ANGLE} to {self.__HARDWARE_MAX_ANGLE} degrees "
                             f"(inclusive)")

        self.__zero_point = zero_position
        self.__min_angle = self.__HARDWARE_MIN_ANGLE - self.__zero_point
        self.__max_angle = self.__HARDWARE_MAX_ANGLE - self.__zero_point

    @property
    def angle_range(self):
        """Returns a tuple with minimum and maximum possible angles where the
        servo horn can be moved to.

        If :class:`zero_point` is set to 0 (default), the angle range
        will be (-90, 90).
        """

        return self.__min_angle, self.__max_angle

    @property
    def setting(self):
        """Returns the current state of the servo motor, giving curent angle
        and current speed.

        :return: :class:'ServoMotorSetting` object that has angle and speed attributes.
        """
        if not self.__has_set_angle:
            return None, None

        angle, speed = self.__controller.get_current_angle_and_speed()
        current_state = ServoMotorSetting()
        current_state.angle = angle - self.zero_point
        current_state.speed = speed
        return current_state

    @setting.setter
    def setting(self, target_state: ServoMotorSetting):
        """Sets the target state of the servo horn, relative to the zero
        position.

           .. warning::
             Using an :data:`target_state.angle` out of the valid angle range will cause the method to raise an
             exception. To determine the valid angle range, use :meth:`ServoMotor.get_angle_range`.

           .. warning::
             Using a :data:`target_state.speed` out of the valid speed range will cause the method to raise an exception.

        :type target_state: :class:`ServoMotorSetting`
        :param target_state:
            Set the target servo state using the :class:`ServoMotorSetting` class, both :meth:`ServoMotorSetting.speed` and
            :meth:`ServoMotorSetting.angle` must be passed. Example usage:

            .. code-block:: python
                from pitop import ServoMotor, ServoMotorSetting
                servo = ServoMotor()
                target_state = ServoMotorSetting()
                target_state.angle = 45
                target_state.speed = 20
                servo.state = target_state
        """
        self.target_angle = target_state.angle
        self.target_speed = target_state.speed

        self.__controller.set_target_angle(target_state.angle + self.__zero_point, target_state.speed)
        self.__has_set_angle = True

    @property
    def current_angle(self):
        """Returns the current angle that the servo motor is at.

           .. note::
             If you need synchronized angle and speed values, use :meth:`ServoMotor.state` instead, this will return both
             current angle and current speed at the same time.

        :return: float value of the current angle of the servo motor in degrees.
        """
        angle, _ = self.__controller.get_current_angle_and_speed()
        return angle - self.zero_point

    @property
    def current_speed(self):
        """Returns the current speed the servo motor is at.

           .. note::
             If you need synchronized angle and speed values, use :meth:`ServoMotor.state` instead, this will return both
             current angle and current speed at the same time.

        :return: float value of the current speed of the servo motor in deg/s.
        """
        _, speed = self.__controller.get_current_angle_and_speed()
        return speed

    @property
    def smooth_acceleration(self):
        """Gets whether or not the servo is configured to use a linear
        acceleration profile to ramp speed at start and end of cycle.

        :return: boolean value of the acceleration mode
        """
        return self.__controller.get_acceleration_mode() == 1

    @smooth_acceleration.setter
    def smooth_acceleration(self, enabled: bool):
        """Sets whether or not the servo is configured to use a linear
        acceleration profile to ramp speed at start and end of cycle.

        :type enabled: bool
        :param enabled: acceleration mode state
        """
        self.__controller.set_acceleration_mode(int(enabled))

    @property
    def target_angle(self):
        """Returns the last target angle that has been set.

        :return: float value of the target angle of the servo motor in deg.
        """
        return self.__target_state.angle

    @target_angle.setter
    def target_angle(self, angle):
        """Set the target angle you want the servo motor to go to.

        :type angle: float
        :param angle: target servo motor angle.
        """
        if not (self.__min_angle <= angle <= self.__max_angle):
            raise ValueError(f"Angle value must be from {self.__min_angle} to {self.__max_angle} degrees (inclusive)")
        self.__target_angle = angle
        self.__controller.set_target_angle(self.__target_angle + self.__zero_point, self.__target_speed)
        self.__has_set_angle = True

    @property
    def target_speed(self):
        """Returns the last target speed that has been set.

        :return: float value of the target speed of the servo motor in deg/s.
        """
        return self.__target_speed

    @target_speed.setter
    def target_speed(self, speed):
        """Sets the servo motor speed. The speed value must be a number from.

        -100.0 to 100.0 deg/s.

           .. warning::
             Using a :data:`speed` out of the valid speed range will cause the method to raise an exception.

        :type speed: int or float
        :param speed:
            The target speed at which to move the servo horn, from -100 to 100 deg/s.
        """
        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")
        self.__target_speed = speed

    def sweep(self, speed=None):
        """Moves the servo horn from the current position to one of the servo
        motor limits (maximum/minimum possible angle), moving at the specified
        speed. The speed value must be a number from -100.0 to 100.0 deg/s.

        The sweep direction is given by the speed.

        Setting a :data:`speed` value higher than zero will move the horn to the maximum angle (90 degrees by default),
        while a value less than zero will move it to the minimum angle (-90 degress by default).

           .. warning::
             Using a :data:`speed` out of the valid speed range will cause the method to raise an exception.

        :type speed: int or float
        :param speed:
            The target speed at which to move the servo horn, from -100 to 100 deg/s.
        """
        speed = self.target_speed if speed is None else speed
        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Speed value must be from {ServoHardwareSpecs.SPEED_RANGE} to {ServoHardwareSpecs.SPEED_RANGE} deg/s (inclusive)")

        angle = self.__min_angle if speed < 0 else self.__max_angle
        self.__controller.set_target_angle(angle + self.__zero_point, speed)
