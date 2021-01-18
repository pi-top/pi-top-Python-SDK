from math import floor, pi

from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
)

from pitop.system.port_manager import PortManager


# Taken from https://github.com/pi-top/pi-top-Robotics-Kit-Python-Examples/blob/main/ptrobot/alex/common/robot_move_controller.py
# Added PortManager section

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
        self._wheel_base = 0.1725
        self._wheel_diameter = 0.074
        self._wheel_circumference = self._wheel_diameter * pi
        self._linear_speed_x = 0
        self._angular_speed_z = 0

        self._left_motor = EncoderMotor(port_name=left_motor_port,
                                        forward_direction=ForwardDirection.CLOCKWISE)
        self._right_motor = EncoderMotor(port_name=right_motor_port,
                                         forward_direction=ForwardDirection.COUNTER_CLOCKWISE)
        self._max_rpm = floor(min(self._left_motor.max_rpm, self._right_motor.max_rpm))

        self._max_speed = self._rpm_to_speed(self._max_rpm)
        self._max_angular_speed = 2 * self._max_speed / self._wheel_base

        self.__port_manager = PortManager()
        self.__port_manager.register_component_instance(self._left_motor, left_motor_port)
        self.__port_manager.register_component_instance(self._right_motor, right_motor_port)

    def command(self, twist_data):
        linear_speed = twist_data.linear.x
        angular_speed = twist_data.angular.z
        self.robot_move(linear_speed, angular_speed)

    def robot_move(self, linear_speed, angular_speed):
        # if angular_speed is positive, then rotation is anti-clockwise in this coordinate frame
        speed_right = linear_speed + (self._wheel_base * angular_speed) / 2
        speed_left = linear_speed - (self._wheel_base * angular_speed) / 2
        rpm_right = self._speed_to_rpm(speed_right)
        rpm_left = self._speed_to_rpm(speed_left)
        rpm_diff = abs(rpm_right - rpm_left)

        if rpm_right > self._max_rpm:
            rpm_right = self._max_rpm
            rpm_left = self._max_rpm - rpm_diff
        elif rpm_right < -self._max_rpm:
            rpm_right = -self._max_rpm
            rpm_left = -self._max_rpm + rpm_diff

        if rpm_left > self._max_rpm:
            rpm_left = self._max_rpm
        elif rpm_left < -self._max_rpm:
            rpm_left = -self._max_rpm

        self._left_motor.set_target_rpm(target_rpm=rpm_left)
        self._right_motor.set_target_rpm(target_rpm=rpm_right)

    def forward(self, speed_factor):
        self._linear_speed_x = self._max_speed * speed_factor
        self.robot_move(self._linear_speed_x, self._angular_speed_z)

    def backward(self, speed_factor):
        self.forward(-speed_factor)

    def left(self, speed_factor):
        self._angular_speed_z = self._max_angular_speed * speed_factor
        self.robot_move(self._linear_speed_x, self._angular_speed_z)

    def right(self, speed_factor):
        self.left(-speed_factor)

    def stop(self):
        self._linear_speed_x = 0
        self._angular_speed_z = 0
        self.robot_move(self._linear_speed_x, self._angular_speed_z)

    def stop_rotation(self):
        self._angular_speed_z = 0
        self.robot_move(self._linear_speed_x, self._angular_speed_z)

    def _speed_to_rpm(self, speed):
        rpm = round(60.0 * speed / self._wheel_circumference, 1)
        return rpm

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self._wheel_circumference / 60.0, 3)
        return speed
