from .parameters import BrakingType, ForwardDirection, Direction
from .encoder_motor_controller import EncoderMotorController

import time
from math import floor, pi
import atexit


class EncoderMotor:
    """
    Represents a pi-top motor encoder component.

    Note that pi-top motor encoders use a built-in closed-loop control system, that feeds the readings
    from an encoder sensor to an PID controller. This controller will actively modify the motor's current to move at the desired
    speed or position, even if a load is applied to the shaft.

    This internal controller is used when moving the motor through :class:`set_target_rpm` or :class:`set_target_speed`
    methods, while using the :class:`set_power` method will make the motor work in open-loop, not using the controller.

    .. note::
        Note that some methods allow to use distance and speed settings in meters and meters per second. These will only make
        sense when using a wheel attached to the shaft of the motor.

        The conversions between angle, rotations and RPM used by the motor to meters and meters/second are performed considering
        the :data:`wheel_diameter` parameter. This parameter defaults to the diameter of the wheel included with MMK.
        If a wheel of different dimmensions is attached to the motor, you'll need to measure it's diameter, in order for these
        methods to work properly.

    :type port_name: str
    :param port_name:
        The ID for the port to which this component is connected.

    :type forward_direction: ForwardDirection
    :param forward_direction:
        The type of rotation of the motor shaft that corresponds to forward motion.

    :type braking_type: BrakingType
    :param braking_type:
        The braking type of the motor. Defaults to coast.

    :type wheel_diameter: int or float
    :param wheel_diameter:
        The diameter of the wheel attached to the motor.
    """

    MMK_STANDARD_GEAR_RATIO = 41.8
    MAX_DC_MOTOR_RPM = 4800

    def __init__(self,
                 port_name,
                 forward_direction,
                 braking_type=BrakingType.COAST,
                 wheel_diameter=0.075
                 ):
        self._pma_port = port_name

        self.__motor_core = EncoderMotorController(self._pma_port, braking_type.value)
        self.__forward_direction = forward_direction
        self.__wheel_diameter = wheel_diameter

        self.__prev_time_dist_cnt = time.time()
        self.__previous_reading_odometer = 0

        atexit.register(self.stop)

    @property
    def forward_direction(self):
        """
        Represents the forward direction setting used by the motor.

        Setting this property will determine on which direction the motor will turn
        whenever a movement in a particular direction is requested.

        :type forward_direction: ForwardDirection
        :param forward_direction:
            The direction that corresponds to forward motion.
        """
        return ForwardDirection(self.__forward_direction)

    @forward_direction.setter
    def forward_direction(self, forward_direction):
        self.__forward_direction = forward_direction

    @property
    def braking_type(self):
        """
        Returns the type of braking used by the motor when it's stopping after a movement.

        Setting this property will change the way the motor stops a movement:

        - :data:`BrakingType.COAST` will make the motor coast to a halt when stopped.
        - :data:`BrakingType.BRAKE` will cause the motor to actively brake when stopped.

        :type braking_type: BrakingType
        :param braking_type:
            The braking type of the motor.
        """
        return BrakingType(self.__motor_core.braking_type())

    @braking_type.setter
    def braking_type(self, braking_type):

        self.__motor_core.set_braking_type(braking_type.value)

    def set_power(self, power, direction=Direction.FORWARD):
        """
        Turn the motor on at the power level provided, in the range -1.0 to +1.0, where:

        - 1.0: motor will turn with full power in the :data:`direction` provided as argument.
        - 0.0: motor will not move.
        - -1.0: motor will turn with full power in the direction contrary to :data:`direction`.

        .. warning::
            Setting a :data:`.power` value out of range will cause the method to raise an
            exception.

        :type power: int or float
        :param power:
            Motor power, in the range -1.0 to +1.0

        :type direction: Direction
        :param direction:
            Direction to rotate the motor
        """

        if not (-1.0 <= power <= 1.0):
            raise ValueError("Power value must be between -1.0 and +1.0 (inclusive)")

        power_mapping = int(round(power * 1000) * self.__forward_direction * direction)

        self.__motor_core.set_power(power_mapping)

    def power(self):
        """
        Get the current power of the motor.

        Returns a value from -1.0 to +1.0, assuming the user is controlling the motor
        using the :class:`set_power` method (motor is in control mode 0).
        If this is not the case, returns None.
        """

        power = self.__motor_core.power()
        if power:
            return power / 1000.0
        return None

    def set_target_rpm(self, target_rpm, direction=Direction.FORWARD, total_rotations=0.0):
        """
        Run the motor at the specified :data:`.target_rpm` RPM.

        If desired, a number of full or partial rotations can also be set through the :data:`total_rotations`
        parameter. Once reached, the motor will stop. Setting :data:`total_rotations` to 0 will set the
        motor to run indefinitely until stopped.

        If the desired RPM setting cannot be achieved, :class:`torque_limited` will be set to :data:`True`
        and the motor will run at the maximum possible RPM it is capable of for the instantaneous torque.
        This means that if the torque lowers, then the RPM will continue to rise until it meets the
        desired level.

        Care needs to be taken here if you want to drive a vehicle forward in a straight line, as the motors
        are not guaranteed to spin at the same rate if they are torque-limited.

        .. warning::
            Setting a :data:`.target_rpm` higher than the maximum allowed will cause the
            method to throw an exception. To determine what the maximum possible target RPM for the motor
            is, use the :class:`max_rpm` method.

        :type target_rpm: int or float
        :param target_rpm:
            Desired RPM of output shaft

        :type direction: Direction
        :param direction:
            Direction to rotate the motor. Defaults to forward.

        :type total_rotations: int or float
        :param total_rotations:
            Total number of rotations to be execute. Set to 0 to run indefinitely.
        """
        dc_motor_rpm = int(round(target_rpm * self.MMK_STANDARD_GEAR_RATIO) * self.__forward_direction * direction)
        dc_motor_rotations = int(round(total_rotations * self.MMK_STANDARD_GEAR_RATIO) * self.__forward_direction * direction)

        if not (-self.MAX_DC_MOTOR_RPM <= dc_motor_rpm <= self.MAX_DC_MOTOR_RPM):
            raise ValueError(f"DC motor RPM value must be between {-self.MAX_DC_MOTOR_RPM} and {self.MAX_DC_MOTOR_RPM} (inclusive)")

        if dc_motor_rotations == 0:
            self.__motor_core.set_rpm_control(dc_motor_rpm)
        else:
            dc_motor_rotation_counter = self.__motor_core.odometer()
            rotations_offset_to_send = int(dc_motor_rotations + dc_motor_rotation_counter)
            self.__motor_core.set_rpm_with_rotations(dc_motor_rpm, rotations_offset_to_send)

    def target_rpm(self):
        """
        Get the desired RPM of the motor output shaft, assuming the user is controlling the motor
        using :class:`set_target_rpm` (motor is in control mode 1). If this is not the case, returns None.
        """

        rpm = self.__motor_core.rpm_control()
        if rpm:
            return rpm / self.MMK_STANDARD_GEAR_RATIO * self.__forward_direction
        return None

    def stop(self):
        """
        Stop the motor in all circumstances.
        """
        self.__motor_core.stop()

    @property
    def current_rpm(self):
        """
        Returns the actual RPM currently being achieved at the output shaft, measured by the encoder sensor.

        .. note::
            Note that this value might differ from the target RPM set through :class:`set_target_rpm`.

        """

        dc_motor_rpm_actual = self.__motor_core.tachometer() * self.__forward_direction
        output_shaft_rpm_actual = dc_motor_rpm_actual / self.MMK_STANDARD_GEAR_RATIO

        return output_shaft_rpm_actual

    @property
    def rotation_counter(self):
        """
        Returns the total or partial number of rotations performed by the motor shaft.

        Rotations will increment when moving forward, and decrement when moving backward.
        This value is a float with many decimal points of accuracy, so can be used to monitor even very small turns of the output shaft.
        """

        dc_motor_rotation_counter = self.__motor_core.odometer() * self.__forward_direction
        output_shaft_rotation_counter = round(dc_motor_rotation_counter / self.MMK_STANDARD_GEAR_RATIO, 1)

        return output_shaft_rotation_counter

    @property
    def torque_limited(self):
        """
        Check if the actual motor speed or RPM does not match the target speed or RPM.
        Returns a boolean value, :data:`True` if the motor is torque-limited and :data:`False` if it is not.
        """

        return False

    @property
    def max_rpm(self):
        """
        Returns the approximate maximum RPM capable given the motor and gear ratio.
        """

        return floor(self.MAX_DC_MOTOR_RPM / self.MMK_STANDARD_GEAR_RATIO)

    @property
    def wheel_diameter(self):
        """
        Represents the diameter of the wheel attached to the motor in meters.

        This parameter is important if using library functions to measure speed or distance, as these rely on
        knowing the diameter of the wheel in order to function correctly.
        Use one of the predefined pi-top wheel and tyre types, or define your own wheel size.

        .. note::
            Note the following diameters:

            - pi-top MMK Standard Wheel: 0.060.0m
            - pi-top MMK Standard Wheel with Rubber Tyre: 0.065m
            - pi-top MMK Standard Wheel with tank track: 0.070m

        :type wheel_diameter: int or float
        :param wheel_diameter:
            Wheel diameter in meters.
        """
        return self.__wheel_diameter

    @wheel_diameter.setter
    def wheel_diameter(self, wheel_diameter):
        if wheel_diameter <= 0.0:
            raise ValueError("Wheel diameter must be higher than 0")

        self.__wheel_diameter = wheel_diameter

    @property
    def wheel_circumference(self):
        return self.wheel_diameter * pi

    def set_target_speed(self, target_speed, direction=Direction.FORWARD, distance=0.0):
        """
        Run the wheel at the specified target speed in meters per second.

        If desired, a :data:`distance` to travel can also be specified in meters, after which the motor
        will stop. Setting :data:`distance` to 0 will set the motor to run indefinitely until stopped.

        .. warning::
            Setting a :data:`.target_speed` higher than the maximum allowed will cause the
            method to throw an exception. To determine what the maximum possible target speed for the motor
            is, use the :class:`max_speed` method.

        .. note::
            Note that for this method to move the wheel the expected :data:`distance`, the correct
            :data:`wheel_diameter` value needs to be used.

        :type target_speed: int or float
        :param target_speed:
            Desired speed in m/s

        :type direction: Direction
        :param direction:
            Direction to rotate the motor. Defaults to forward.

        :type distance: int or float
        :param distance:
            Total distance to travel in m. Set to 0 to run indefinitely.
        """
        if not (-self.max_speed <= target_speed <= self.max_speed):
            raise ValueError(f"Wheel speed value must be between {-self.max_speed} and {self.max_speed} (inclusive)")

        rpm = 60.0 * (target_speed / self.wheel_circumference)
        total_rotations = distance / self.wheel_circumference

        self.set_target_rpm(rpm, direction, total_rotations)

    def forward(self, target_speed, distance=0.0):
        """
        Run the wheel forward at the desired speed in meters per second.

        This method is a simple interface to move the motor that wraps a call to :data:`set_target_speed`,
        specifying the forward direction.

        If desired, a :data:`distance` to travel can also be specified in meters, after which the motor
        will stop. Setting :data:`distance` to 0 will set the motor to run indefinitely until stopped.

        .. note::
            Note that for this method to move the wheel the expected :data:`distance`, the correct
            :data:`wheel_circumference` value needs to be used.

        :type target_speed: int or float
        :param target_speed:
            Desired speed in m/s

        :type distance: int or float
        :param distance:
            Total distance to travel in m. Set to 0 to run indefinitely.
        """

        self.set_target_speed(target_speed, Direction.FORWARD, distance)

    def backward(self, target_speed, distance=0.0):
        """
        Run the wheel backwards at the desired speed in meters per second.

        This method is a simple interface to move the wheel that wraps a call to :data:`set_target_speed`,
        specifying the back direction.

        If desired, a :data:`distance` to travel can also be specified in meters, after which the motor
        will stop. Setting :data:`distance` to 0 will set the motor to run indefinitely until stopped.

        .. note::
            Note that for this method to move the wheel the expected :data:`distance`, the correct
            :data:`wheel_circumference` value needs to be used.

        :type target_speed: int or float
        :param target_speed:
            Desired speed in m/s

        :type distance: int or float
        :param distance:
            Total distance to travel in m. Set to 0 to run indefinitely.
        """

        self.set_target_speed(target_speed, Direction.BACK, distance)

    @property
    def current_speed(self):
        """
        Returns the speed currently being achieved by the motor in meters per second.

        .. note::
            Note that this value might differ from the target speed set through :class:`set_target_speed`.
        """

        return (self.current_rpm / 60.0) * self.wheel_circumference

    @property
    def distance(self):
        """
        Returns the distance the wheel has travelled in meters.

        .. note::
            Note that this value depends on using the correct :data:`wheel_circumference` value
        """

        return self.wheel_circumference * self.rotation_counter

    @property
    def max_speed(self):
        """
        The approximate maximum speed possible for the wheel attached to the motor shaft, given the motor
        specs, gear ratio and wheel circumference.

        .. note::
            Note that this value depends on using the correct :data:`wheel_circumference` value
        """

        return self.max_rpm / 60.0 * self.wheel_circumference
