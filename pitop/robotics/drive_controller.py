from math import (
    floor,
    pi,
    radians,
)
from time import sleep

from simple_pid import PID

from pitop.core.exceptions import UninitializedComponent
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
)


class DriveController(Stateful, Recreatable):
    """Represents a vehicle with two wheels connected by an axis, and an
    optional support wheel or caster."""
    _initialized = False

    def __init__(self, left_motor_port="M3", right_motor_port="M0", name="drive"):
        self.name = name
        self.right_motor_port = right_motor_port
        self.left_motor_port = left_motor_port

        self._wheel_separation = 0.1675
        self._wheel_diameter = 0.074
        self._wheel_circumference = self._wheel_diameter * pi
        self._linear_speed_x_hold = 0

        self._left_motor_port = left_motor_port
        self._right_motor_port = right_motor_port

        self.left_motor = EncoderMotor(port_name=left_motor_port,
                                       forward_direction=ForwardDirection.CLOCKWISE)
        self.right_motor = EncoderMotor(port_name=right_motor_port,
                                        forward_direction=ForwardDirection.COUNTER_CLOCKWISE)

        self._max_motor_rpm = floor(min(self.left_motor.max_rpm, self.right_motor.max_rpm))

        self._max_motor_speed = self._rpm_to_speed(self._max_motor_rpm)
        self._max_robot_angular_speed = self._max_motor_speed / (self._wheel_separation / 2)

        self.__target_lock_pid_controller = PID(Kp=0.045,
                                                Ki=0.002,
                                                Kd=0.0035,
                                                setpoint=0,
                                                output_limits=(-self._max_robot_angular_speed,
                                                               self._max_robot_angular_speed)
                                                )

        self._initialized = True

        Stateful.__init__(self, children=['left_motor', 'right_motor'])
        Recreatable.__init__(self, config_dict={"left_motor_port": left_motor_port,
                                                "right_motor_port": right_motor_port,
                                                "name": self.name})

    def is_initialized(fcn):
        def check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise UninitializedComponent("DriveController not initialized")
            return fcn(self, *args, **kwargs)
        return check_initialization

    def _calculate_motor_rpms(self, linear_speed, angular_speed, turn_radius):
        # if angular_speed is positive, then rotation is anti-clockwise in this coordinate frame
        speed_right = linear_speed + (turn_radius + self._wheel_separation / 2) * angular_speed
        speed_left = linear_speed + (turn_radius - self._wheel_separation / 2) * angular_speed
        rpm_right = self._speed_to_rpm(speed_right)
        rpm_left = self._speed_to_rpm(speed_left)

        if abs(rpm_right) > self._max_motor_rpm or abs(rpm_left) > self._max_motor_rpm:
            factor = self._max_motor_rpm / max(abs(rpm_left), abs(rpm_right))
            rpm_right = rpm_right * factor
            rpm_left = rpm_left * factor

        return rpm_left, rpm_right

    @is_initialized
    def robot_move(self, linear_speed, angular_speed, turn_radius=0.0):
        # TODO: turn_radius will introduce a hidden linear speed component to the robot, so params are syntactically
        #  misleading
        rpm_left, rpm_right = self._calculate_motor_rpms(linear_speed, angular_speed, turn_radius)
        self.left_motor.set_target_rpm(target_rpm=rpm_left)
        self.right_motor.set_target_rpm(target_rpm=rpm_right)

    @is_initialized
    def forward(self, speed_factor, hold=False):
        """Move the robot forward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move backwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        linear_speed_x = self._max_motor_speed * speed_factor
        if hold:
            self._linear_speed_x_hold = linear_speed_x
        else:
            self._linear_speed_x_hold = 0
        self.robot_move(linear_speed_x, 0)

    @is_initialized
    def backward(self, speed_factor, hold=False):
        """Move the robot backward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move forwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        self.forward(-speed_factor, hold)

    @is_initialized
    def left(self, speed_factor, turn_radius=0):
        """Make the robot move to the left, using a circular trajectory.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn right.
        :param float turn_radius:
            Radius used by the robot to perform the movement. Using `turn_radius=0` will cause the robot to rotate in place.
        """

        self.robot_move(self._linear_speed_x_hold, self._max_robot_angular_speed * speed_factor, turn_radius)

    @is_initialized
    def right(self, speed_factor, turn_radius=0):
        """Make the robot move to the right, using a circular trajectory.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn left.
        :param float turn_radius:
            Radius used by the robot to perform the movement. Using `turn_radius=0` will cause the robot to rotate in place.
        """

        self.left(-speed_factor, -turn_radius)

    def target_lock_drive_angle(self, angle):
        """Make the robot move in the direction of the specified angle, while
        maintaining the current linear speed."""
        angular_speed = self.__target_lock_pid_controller(angle)
        self.robot_move(self._linear_speed_x_hold, angular_speed)

    @is_initialized
    def rotate(self, angle, time_to_take):
        """Rotate the robot in place by a given angle and stop.

        :param float angle: Angle of the turn.
        :param float time_to_take: Expected duration of the rotation, in seconds.
        """
        assert time_to_take > 0.0
        angle_radians = radians(angle)
        angular_speed = angle_radians / time_to_take

        angular_speed = angular_speed * angle / abs(angle)
        rpm_left, rpm_right = self._calculate_motor_rpms(0, angular_speed, turn_radius=0)
        rotations = abs(angle) * pi * self._wheel_separation / (360 * self._wheel_circumference)
        self.left_motor.set_target_rpm(target_rpm=rpm_left,
                                       total_rotations=rotations * rpm_left / abs(rpm_left))
        self.right_motor.set_target_rpm(target_rpm=rpm_right,
                                        total_rotations=rotations * rpm_right / abs(rpm_right))
        sleep(time_to_take)

    def stop(self):
        """Stop any movement being performed by the motors."""
        self._linear_speed_x_hold = 0
        self.robot_move(0, 0)

    def stop_rotation(self):
        """Stop any angular movement performed by the robot.

        In the case where linear and rotational movements are being
        performed at the same time (e.g.: during a left turn with a turn
        radius different to 0), calling this method will cause the robot
        to continue the linear movement, so it will continue to move
        forward.
        """
        self.robot_move(self._linear_speed_x_hold, 0)

    def _speed_to_rpm(self, speed):
        rpm = round(60.0 * speed / self._wheel_circumference, 1)
        return rpm

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self._wheel_circumference / 60.0, 3)
        return speed

    @property
    def wheel_separation(self):
        return self._wheel_separation
