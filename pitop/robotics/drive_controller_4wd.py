from math import floor
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
    BrakingType,
)
import numpy as np


class DriveController4WD(Stateful, Recreatable):
    """Represents a vehicle with four mecanum wheels."""
    _initialized = False

    def __init__(self,
                 front_left_motor_port="M2",
                 front_right_motor_port="M1",
                 rear_left_motor_port="M3",
                 rear_right_motor_port="M0",
                 name="drive"
                 ):
        self.name = name
        self.front_left_motor_port = front_left_motor_port
        self.front_right_motor_port = front_right_motor_port
        self.rear_left_motor_port = rear_left_motor_port
        self.rear_right_motor_port = rear_right_motor_port

        # Robot dimensions
        self._wheel_diameter = 0.1
        self.half_wheel_separation_x = 0.18 / 2
        self.half_wheel_separation_y = 0.168 / 2

        # Matrix to convert robot twist commands (v_x, v_y, w_z) to individual mecanum wheel speeds
        self._command_to_wheel_speed_transform = np.array(
            [
                [1, -1, -(self.half_wheel_separation_y + self.half_wheel_separation_x)],  # front left
                [1, 1, (self.half_wheel_separation_y + self.half_wheel_separation_x)],  # front right
                [1, 1, -(self.half_wheel_separation_y + self.half_wheel_separation_x)],  # rear left
                [1, -1, (self.half_wheel_separation_y + self.half_wheel_separation_x)]  # rear right
            ]
        )

        # Motor initialization
        self.front_left_motor = EncoderMotor(port_name=front_left_motor_port,
                                             forward_direction=ForwardDirection.CLOCKWISE,
                                             wheel_diameter=self._wheel_diameter,
                                             braking_type=BrakingType.COAST)
        self.front_right_motor = EncoderMotor(port_name=front_right_motor_port,
                                              forward_direction=ForwardDirection.COUNTER_CLOCKWISE,
                                              wheel_diameter=self._wheel_diameter,
                                              braking_type=BrakingType.COAST)
        self.rear_left_motor = EncoderMotor(port_name=rear_left_motor_port,
                                            forward_direction=ForwardDirection.CLOCKWISE,
                                            wheel_diameter=self._wheel_diameter,
                                            braking_type=BrakingType.COAST)
        self.rear_right_motor = EncoderMotor(port_name=rear_right_motor_port,
                                             forward_direction=ForwardDirection.COUNTER_CLOCKWISE,
                                             wheel_diameter=self._wheel_diameter,
                                             braking_type=BrakingType.COAST)

        # Maximum speeds
        self.max_wheel_speed = floor(min(self.front_left_motor.max_speed,
                                         self.front_right_motor.max_speed,
                                         self.rear_left_motor.max_speed,
                                         self.rear_right_motor.max_speed
                                         ) * 1000
                                     ) / 1000
        self.max_robot_angular_speed = floor(
            self.max_wheel_speed / (self.half_wheel_separation_x + self.half_wheel_separation_y) * 100
        ) / 100

        # Speed hold variables
        self._linear_speed_x_hold = 0
        self._linear_speed_y_hold = 0

        Stateful.__init__(self, children=['front_left_motor',
                                          'front_right_motor',
                                          'rear_left_motor',
                                          'rear_right_motor'
                                          ]
                          )
        Recreatable.__init__(self, config_dict={"front_left_motor_port": front_left_motor_port,
                                                "front_right_motor_port": front_right_motor_port,
                                                "rear_left_motor_port": rear_left_motor_port,
                                                "rear_right_motor_port": rear_right_motor_port,
                                                "name": self.name})

    def _calculate_motor_speeds(self, twist_array):
        motor_speeds = self._command_to_wheel_speed_transform.dot(twist_array)

        scaler = abs(motor_speeds[np.argmax(np.absolute(motor_speeds)), 0] / self.max_wheel_speed)

        if scaler > 1.0:
            # if any desired motor speed is above the maximum speed, scale all motor speeds
            motor_speeds /= scaler

        return motor_speeds.T[0]

    def robot_move(self, linear_x: float = 0.0, linear_y: float = 0.0, angular_z: float = 0.0):
        velocity_array = np.array([[linear_x], [linear_y], [angular_z]])
        speed_front_left, speed_front_right, speed_rear_left, speed_rear_right = self._calculate_motor_speeds(
            velocity_array)
        self.front_left_motor.set_target_speed(target_speed=speed_front_left)
        self.front_right_motor.set_target_speed(target_speed=speed_front_right)
        self.rear_left_motor.set_target_speed(target_speed=speed_rear_left)
        self.rear_right_motor.set_target_speed(target_speed=speed_rear_right)

    def forward(self, speed_factor, hold=False):
        """Move the robot forward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move backwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        linear_speed_x = self.max_wheel_speed * speed_factor
        if hold:
            self._linear_speed_x_hold = linear_speed_x
        else:
            self._linear_speed_x_hold = 0.0
        self.robot_move(linear_x=linear_speed_x, linear_y=self._linear_speed_y_hold, angular_z=0.0)

    def backward(self, speed_factor, hold=False):
        """Move the robot backward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move forwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        self.forward(-speed_factor, hold)

    # TODO: decide whether to change the API (2WD vs 4WD) and call this "turn_left" so "left" is reserved for strafe
    def left(self, speed_factor):
        """Make the robot turn to the left.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the angular velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn right.
        """

        self.robot_move(linear_x=self._linear_speed_x_hold,
                        linear_y=self._linear_speed_y_hold,
                        angular_z=self.max_robot_angular_speed * speed_factor
                        )

    def right(self, speed_factor):
        """Make the robot turn to the right.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the angular velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn left.
        """

        self.left(-speed_factor)

    def left_strafe(self, speed_factor, hold=False):
        linear_speed_y = self.max_wheel_speed * speed_factor
        if hold:
            self._linear_speed_y_hold = linear_speed_y
        else:
            self._linear_speed_y_hold = 0.0
        self.robot_move(linear_x=self._linear_speed_x_hold, linear_y=linear_speed_y, angular_z=0.0)

    def right_strafe(self, speed_factor, hold=False):
        self.left_strafe(-speed_factor, hold=hold)

    def stop(self):
        """Stop any movement being performed by the motors."""
        self._linear_speed_x_hold = 0
        self._linear_speed_y_hold = 0
        self.robot_move(0, 0, 0)

    def stop_rotation(self):
        """Stop any angular movement performed by the robot.

        In the case where linear and rotational movements are being
        performed at the same time, calling this method will cause the robot
        to continue the linear movement, so it will continue to move
        forward.
        """
        self.robot_move(linear_x=self._linear_speed_x_hold, linear_y=self._linear_speed_y_hold, angular_z=0)
