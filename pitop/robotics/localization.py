from threading import Thread
import time
import math
from pitop.core.exceptions import UninitializedComponent
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
)
from pitop.processing.algorithms import EKF, ArucoMarkers

import numpy as np


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Localization(Stateful, Recreatable):
    """
    :param str left_motor_port: Port where the left wheel motor is connected.
    :param str right_motor_port: Port where the right wheel motor is connected.

    """
    _initialized = False

    def __init__(self, left_motor_port="M3", right_motor_port="M0", name="localization"):
        self.name = name

        self._left_motor = EncoderMotor(port_name=left_motor_port,
                                        forward_direction=ForwardDirection.CLOCKWISE)
        self._right_motor = EncoderMotor(port_name=right_motor_port,
                                         forward_direction=ForwardDirection.COUNTER_CLOCKWISE)
        self._robot_x_position = 0
        self._robot_y_position = 0
        self._robot_angle = 0
        self._odom_update_frequency = 5  # Hz

        self._ekf = None
        self._aruco = None

        self._initialized = True

        Stateful.__init__(self, children=['left_motor', 'right_motor'])
        Recreatable.__init__(self, config_dict={"left_motor_port": left_motor_port,
                                                "right_motor_port": right_motor_port,
                                                "name": self.name})

    def is_initialized(fcn):
        def check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise UninitializedComponent("Localization not initialized")
            return fcn(self, *args, **kwargs)
        return check_initialization

    @is_initialized
    def track_position(self):
        self._ekf = EKF()
        self._aruco = ArucoMarkers()
        odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        odometry_tracker.start()

    def __track_odometry(self):
        prev_time = time.time()
        theta_r = 0
        while True:
            current_time = time.time()
            dt = current_time - prev_time
            if dt >= 1.0/self._odom_update_frequency:
                prev_time = current_time
                left_wheel_speed = self._left_motor.current_speed

                right_wheel_speed = self._right_motor.current_speed

                robot_pose_observation = None
                if self._aruco.detect(self.camera.get_frame()):
                    robot_pose_observation = self._aruco.get_camera_pose()

                v_rx = (right_wheel_speed + left_wheel_speed) / 2
                # v_ry = 0  # cannot move in y
                omega_r = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation  # in rad/s
                theta_r += omega_r * dt
                v_wx = v_rx * math.cos(theta_r)  # - v_ry * math.sin(theta_r) - these terms are zero
                v_wy = v_rx * math.sin(theta_r)  # + v_ry * math.cos(theta_r) - these terms are zero
                theta_dot_w = omega_r
                self._robot_x_position += v_wx * dt
                self._robot_y_position += v_wy * dt
                self._robot_angle += math.degrees(theta_dot_w * dt)
                self._robot_angle %= 360  # give angle from 0 to 360
                u = np.array([[v_rx, omega_r]]).T
                self._ekf.update(u, robot_pose_observation)
            else:
                continue

    @property
    def position(self):
        return DotDict({
            'x': self._robot_x_position,
            'y': self._robot_y_position,
            'angle': self._robot_angle
        })

    @property
    def position_update_frequency(self):
        return self._odom_update_frequency

    @position_update_frequency.setter
    def position_update_frequency(self, value: int):
        self._odom_update_frequency = value
