import logging
from math import copysign, floor, radians
from time import sleep
from typing import Optional, Union

from pitop.core.mixins import Recreatable, Stateful
from pitop.pma import EncoderMotor, ForwardDirection
from pitop.pma.common.encoder_motor_registers import MotorSyncBits, MotorSyncRegisters
from pitop.pma.plate_interface import PlateInterface

from .simple_pid import PID

logger = logging.getLogger(__name__)


POST_WRITE_SLEEP = 0.02


class DriveController(Stateful, Recreatable):
    """Represents a vehicle with two wheels connected by an axis, and an
    optional support wheel or caster."""

    def __init__(
        self,
        left_motor_port: str = "M3",
        right_motor_port: str = "M0",
        name: str = "drive",
    ):
        self.name = name

        # motor and wheel setup
        self.left_motor_port = left_motor_port
        self.right_motor_port = right_motor_port
        self.left_motor = EncoderMotor(
            port_name=self.left_motor_port, forward_direction=ForwardDirection.CLOCKWISE
        )
        self.right_motor = EncoderMotor(
            port_name=self.right_motor_port,
            forward_direction=ForwardDirection.COUNTER_CLOCKWISE,
        )

        # chassis setup
        self.wheel_separation = 0.163

        # Round down to ensure no speed value ever goes above maximum due to rounding issues (resulting in error)
        self.max_motor_speed = (
            floor(min(self.left_motor.max_speed, self.right_motor.max_speed) * 1000)
            / 1000
        )
        self.max_robot_angular_speed = self.max_motor_speed / (
            self.wheel_separation / 2
        )

        # Target lock drive angle
        self._linear_speed_x_hold = 0
        self.__target_lock_pid_controller = PID(
            Kp=0.045,
            Ki=0.002,
            Kd=0.0035,
            setpoint=0,
            output_limits=(-self.max_robot_angular_speed, self.max_robot_angular_speed),
        )

        # Motor syncing
        self.__mcu_device = PlateInterface().get_device_mcu()

        Stateful.__init__(self, children=["left_motor", "right_motor"])
        Recreatable.__init__(
            self,
            config_dict={
                "left_motor_port": left_motor_port,
                "right_motor_port": right_motor_port,
                "name": self.name,
            },
        )

    def _set_synchronous_motor_movement_mode(self) -> None:
        sync_config = (
            MotorSyncBits[self.left_motor_port].value
            | MotorSyncBits[self.right_motor_port].value
        )
        self.__mcu_device.write_byte(MotorSyncRegisters.CONFIG.value, sync_config)
        sleep(POST_WRITE_SLEEP)

    def _unset_synchronous_motor_movement_mode(self) -> None:
        self.__mcu_device.write_byte(MotorSyncRegisters.CONFIG.value, 0b0000000)
        sleep(POST_WRITE_SLEEP)

    def _start_synchronous_motor_movement(self) -> None:
        self.__mcu_device.write_byte(MotorSyncRegisters.START.value, 1)
        sleep(POST_WRITE_SLEEP)

    def _calculate_motor_speeds(
        self,
        linear_speed: Union[int, float],
        angular_speed: Union[int, float],
        turn_radius: Union[int, float],
    ) -> tuple:
        # if angular_speed is positive, then rotation is anti-clockwise in this coordinate frame
        speed_right = (
            linear_speed + (turn_radius + self.wheel_separation / 2) * angular_speed
        )

        speed_left = (
            linear_speed + (turn_radius - self.wheel_separation / 2) * angular_speed
        )

        if (
            abs(speed_right) > self.max_motor_speed
            or abs(speed_left) > self.max_motor_speed
        ):
            factor = self.max_motor_speed / max(abs(speed_left), abs(speed_right))
            speed_right = speed_right * factor
            speed_left = speed_left * factor

        return speed_left, speed_right

    def robot_move(
        self,
        linear_speed: Union[int, float],
        angular_speed: Union[int, float],
        turn_radius: Union[int, float] = 0.0,
        distance: Optional[Union[int, float]] = None,
    ) -> None:
        # TODO: turn_radius will introduce a hidden linear speed component to the robot, so params are syntactically
        #  misleading
        speed_left, speed_right = self._calculate_motor_speeds(
            linear_speed, angular_speed, turn_radius
        )
        self._set_motor_speeds(speed_left, speed_right, distance)

    def forward(
        self,
        speed_factor: Union[int, float],
        hold: bool = False,
        distance: Optional[Union[int, float]] = None,
    ) -> None:
        """Move the robot forward.

        :param float speed_factor: Factor relative to the maximum motor
            speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move
            backwards.
        :param bool hold: Setting this parameter to true will cause
            subsequent movements to use the speed set as the base speed.
        :param float distance: Distance to travel in meters. If not
            provided, the robot will move indefinitely
        """
        linear_speed_x = self.max_motor_speed * speed_factor
        if hold:
            self._linear_speed_x_hold = linear_speed_x
        else:
            self._linear_speed_x_hold = 0
        self.robot_move(linear_speed=linear_speed_x, angular_speed=0, distance=distance)

    def backward(
        self,
        speed_factor: Union[int, float],
        hold: bool = False,
        distance: Optional[Union[int, float]] = None,
    ) -> None:
        """Move the robot backward.

        :param float speed_factor: Factor relative to the maximum motor
            speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move forwards.
        :param bool hold: Setting this parameter to true will cause
            subsequent movements to use the speed set as the base speed.
        :param float distance: Distance to travel in meters. If not
            provided, the robot will move indefinitely
        """
        self.forward(-speed_factor, hold, distance)

    def left(
        self,
        speed_factor: Union[int, float],
        turn_radius: Union[int, float] = 0,
        distance: Optional[Union[int, float]] = None,
    ) -> None:
        """Make the robot move to the left, using a circular trajectory.

        :param float speed_factor: Factor relative to the maximum motor
            speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn right.
        :param float turn_radius: Radius used by the robot to perform
            the movement. Using `turn_radius=0` will cause the robot to
            rotate in place.
        :param float distance: Distance to travel in meters. If not
            provided, the robot will move indefinitely
        """

        self.robot_move(
            linear_speed=self._linear_speed_x_hold,
            angular_speed=self.max_robot_angular_speed * speed_factor,
            turn_radius=turn_radius,
            distance=distance,
        )

    def right(
        self,
        speed_factor: Union[int, float],
        turn_radius: Union[int, float] = 0,
        distance: Optional[Union[int, float]] = None,
    ) -> None:
        """Make the robot move to the right, using a circular trajectory.

        :param float speed_factor: Factor relative to the maximum motor
            speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn left.
        :param float turn_radius: Radius used by the robot to perform
            the movement. Using `turn_radius=0` will cause the robot to
            rotate in place.
        :param float distance: Distance to travel in meters. If not
            provided, the robot will move indefinitely
        """

        self.left(-speed_factor, -turn_radius, distance)

    def target_lock_drive_angle(self, angle: Union[int, float]) -> None:
        """Make the robot move in the direction of the specified angle, while
        maintaining the current linear speed."""
        angular_speed = self.__target_lock_pid_controller(angle)
        self.robot_move(self._linear_speed_x_hold, angular_speed)

    def rotate(
        self,
        angle: Union[int, float],
        time_to_take: Optional[Union[int, float]] = None,
        max_speed_factor: float = 0.3,
    ) -> None:
        """Rotate the robot in place by a given angle and stop.

        :param float angle: Angle of the turn.
        :param float time_to_take: Expected duration of the rotation, in
            seconds. If not provided, the motors will perform the
            rotation using % of the maximum angular speed allowed by the
            motors, to ensure the robot can perform the rotation without
            issues.
        :param bool max_speed_factor: Factor relative to the maximum
            motor speed, used to set the velocity, in the range 0 to
            1.0.
        """

        assert 0 <= max_speed_factor <= 1.0
        if max_speed_factor > 0.3:
            logger.warning(
                "Using max_speed_factor higher than 0.3 might cause the robot to rotate inconsistently."
            )

        MAX_ANGULAR_SPEED_FOR_ROTATION = self.max_robot_angular_speed * max_speed_factor

        angle_radians = radians(angle)
        if time_to_take is None:
            time_to_take = abs(angle_radians) / MAX_ANGULAR_SPEED_FOR_ROTATION

        assert time_to_take > 0.0
        angular_speed = angle_radians / time_to_take

        if time_to_take and angular_speed > MAX_ANGULAR_SPEED_FOR_ROTATION:
            new_time_to_take = abs(angle_radians) / MAX_ANGULAR_SPEED_FOR_ROTATION

            time_to_take_warning = f"Provided time '{time_to_take}s' is too fast for current max_speed_factor {max_speed_factor};"
            time_to_take_warning += f" using {new_time_to_take}s instead."
            if max_speed_factor < 1:
                time_to_take_warning = f"{time_to_take_warning} Pass a higher max_speed_factor to `rotate()` to use a lower time_to_take."
            logger.warning(time_to_take_warning)

            time_to_take = new_time_to_take
            angular_speed = MAX_ANGULAR_SPEED_FOR_ROTATION

        speed_left, speed_right = self._calculate_motor_speeds(
            linear_speed=0, angular_speed=angular_speed, turn_radius=0
        )

        self._set_motor_speeds(
            speed_left,
            speed_right,
            distance=abs(angle_radians) * self.wheel_separation / 2,
        )
        sleep(time_to_take)

    def stop(self) -> None:
        """Stop any movement being performed by the motors."""
        self._linear_speed_x_hold = 0
        self.robot_move(0, 0)

    def stop_rotation(self) -> None:
        """Stop any angular movement performed by the robot.

        In the case where linear and rotational movements are being
        performed at the same time (e.g.: during a left turn with a turn
        radius different to 0), calling this method will cause the robot
        to continue the linear movement, so it will continue to move
        forward.
        """
        self.robot_move(self._linear_speed_x_hold, 0)

    def _set_motor_speeds(
        self, left_speed: float, right_speed: float, distance: Optional[float] = None
    ) -> None:
        """Set the speed of the left and right motors.

        :param float left_speed: Speed for the left motor.
        :param float right_speed: Speed for the right motor.
        :param float distance: Distance to travel in meters.
        """
        if distance is None:
            # run indefinitely
            distance = 0.0
        self._set_synchronous_motor_movement_mode()
        self.left_motor.set_target_speed(
            left_speed, distance=copysign(distance, left_speed)
        )
        self.right_motor.set_target_speed(
            right_speed, distance=copysign(distance, right_speed)
        )
        self._start_synchronous_motor_movement()
        self._unset_synchronous_motor_movement_mode()
