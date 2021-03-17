from threading import Thread
import time
import math
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


class Localization:
    """

    """

    def __init__(self, robot):
        self._camera = robot.camera
        self._drive_controller = robot.drive_controller
        # self._left_motor = left_motor
        # self._right_motor = right_motor
        self._robot_x_position = 0
        self._robot_y_position = 0
        self._robot_angle = 0
        self._odom_update_frequency = 5  # Hz

        self._ekf = None
        self._aruco = None

    def start(self):
        self._ekf = EKF()
        self._aruco = ArucoMarkers()
        odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        odometry_tracker.start()

    def __track_odometry(self):
        prev_time = time.time()
        u_k = np.zeros((2, 1))
        while True:
            current_time = time.time()
            dt = current_time - prev_time
            if dt >= 1.0/self._odom_update_frequency:
                prev_time = current_time

                left_wheel_speed = self._drive_controller._left_motor.current_speed

                right_wheel_speed = self._drive_controller._right_motor.current_speed

                # print(f'left_wheel_speed: {left_wheel_speed:2f}')

                # robot_pose_observation = None
                # if self._aruco.detect(self._camera.get_frame()):
                #     robot_pose_observation = self._aruco.get_camera_pose()

                v_rx = (right_wheel_speed + left_wheel_speed) / 2.0
                # v_ry = 0  # cannot move in y
                omega_r = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation  # in rad/s

                u_k[0][0] = v_rx
                u_k[1][0] = omega_r

                z_k = None
                if self._aruco.detect(self._camera.get_frame()):
                    camera_poses = self._aruco.get_camera_pose()

                self._ekf.update(u_k, z_k, dt)

                pose_mean = self._ekf.pose_mean
                pose_covariance = self._ekf.pose_covariance

                det = np.linalg.det(pose_covariance)

                print(f'pose: {pose_mean}')
                print(f'det: {det:2f}')






                # theta_r += omega_r * dt
                # v_wx = v_rx * math.cos(theta_r)  # - v_ry * math.sin(theta_r) - these terms are zero
                # v_wy = v_rx * math.sin(theta_r)  # + v_ry * math.cos(theta_r) - these terms are zero
                # theta_dot_w = omega_r
                # self._robot_x_position += v_wx * dt
                # self._robot_y_position += v_wy * dt
                # self._robot_angle += math.degrees(theta_dot_w * dt)
                # self._robot_angle %= 360  # give angle from 0 to 360
                # u = np.array([[v_rx, omega_r]]).T
                # self._ekf.update(u, robot_pose_observation)
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
