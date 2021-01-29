from math import floor, pi

from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
)

from pitop.system.port_manager import PortManager
from .pid_controller import PIDController


class DriveController:
    """
    Robot reference coordinate system:
        linear
            x = forward
            y = left
            z = up
        angular:
            x = roll
            y = pitch
            z = yaw
            Positive and negative directions of angular velocities use the right hand rule
            e.g. positive angular z velocity is a rotation of the robot anti-clockwise
    """

    def __init__(self, left_motor_port="M3", right_motor_port="M0"):
        # TODO: increase accuracy of wheel_base and wheel_diameter with empirical testing
        self._wheel_separation = 0.1725
        self._wheel_diameter = 0.074
        self._wheel_circumference = self._wheel_diameter * pi
        self._linear_speed_x_hold = 0

        self._left_motor = EncoderMotor(port_name=left_motor_port,
                                        forward_direction=ForwardDirection.CLOCKWISE)
        self._right_motor = EncoderMotor(port_name=right_motor_port,
                                         forward_direction=ForwardDirection.COUNTER_CLOCKWISE)
        self._max_motor_rpm = floor(min(self._left_motor.max_rpm, self._right_motor.max_rpm))

        self._max_motor_speed = self._rpm_to_speed(self._max_motor_rpm)
        self._max_robot_angular_speed = self._max_motor_speed / (self._wheel_separation / 2)

        self.__port_manager = PortManager()
        self.__port_manager.register_pma_component(self._left_motor)
        self.__port_manager.register_pma_component(self._right_motor)

        self.__target_lock_pid_controller = PIDController(lower_limit=-self._max_robot_angular_speed,
                                                          upper_limit=self._max_robot_angular_speed,
                                                          setpoint=0,
                                                          Kp=0.045,
                                                          Ki=0.002,
                                                          Kd=0.0035)

    def __calculate_motor_rpms(self, linear_speed, angular_speed, turn_radius):
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

    def __robot_move(self, linear_speed, angular_speed, turn_radius=0.0):
        # TODO: turn_radius will introduce a hidden linear speed component to the robot, so params are syntactically
        #  misleading
        rpm_left, rpm_right = self.__calculate_motor_rpms(linear_speed, angular_speed, turn_radius)
        self._left_motor.set_target_rpm(target_rpm=rpm_left)
        self._right_motor.set_target_rpm(target_rpm=rpm_right)

    def forward(self, speed_factor, hold):
        linear_speed_x = self._max_motor_speed * speed_factor
        if hold:
            self._linear_speed_x_hold = linear_speed_x
        else:
            self._linear_speed_x_hold = 0
        self.__robot_move(linear_speed_x, 0)

    def backward(self, speed_factor, hold):
        self.forward(-speed_factor, hold)

    def left(self, speed_factor, turn_radius):
        self.__robot_move(self._linear_speed_x_hold, self._max_robot_angular_speed * speed_factor, turn_radius)

    def right(self, speed_factor, turn_radius):
        self.left(-speed_factor, turn_radius)

    def target_lock_drive_angle(self, angle):
        angular_speed = self.__target_lock_pid_controller.control_state_update(angle)
        self.__robot_move(self._linear_speed_x_hold, angular_speed)

    def rotate(self, angle, angular_speed):
        angular_speed = angular_speed * angle / abs(angle)
        rpm_left, rpm_right = self.__calculate_motor_rpms(0, angular_speed, turn_radius=0)
        rotations = abs(angle) * pi * self._wheel_separation / (360 * self._wheel_circumference)
        self._left_motor.set_target_rpm(target_rpm=rpm_left,
                                        total_rotations=rotations*rpm_left/abs(rpm_left))
        self._right_motor.set_target_rpm(target_rpm=rpm_right,
                                         total_rotations=rotations*rpm_right/abs(rpm_right))

    def stop(self):
        self._linear_speed_x_hold = 0
        self.__robot_move(0, 0)

    def stop_rotation(self):
        self.__robot_move(self._linear_speed_x_hold, 0)

    def _speed_to_rpm(self, speed):
        rpm = round(60.0 * speed / self._wheel_circumference, 1)
        return rpm

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self._wheel_circumference / 60.0, 3)
        return speed
