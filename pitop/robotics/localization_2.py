from threading import Thread
import time
import math
from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
)
from pitop.processing.algorithms import EKF, ArucoMarkers

import numpy as np

import cv2


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])


class Localization:
    """

    """

    def __init__(self, robot):
        self._camera = robot.camera
        self._drive_controller = robot.drive
        # self._left_motor = left_motor
        # self._right_motor = right_motor
        self._robot_x_position = 0
        self._robot_y_position = 0
        self._robot_angle = 0
        self._odom_update_frequency = 5  # Hz

        self._ekf = None
        self._aruco = None
        self._frame = None

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
            if dt >= 1.0 / self._odom_update_frequency:
                prev_time = current_time

                left_wheel_speed = self._drive_controller.left_motor.current_speed

                right_wheel_speed = self._drive_controller.right_motor.current_speed

                # print(f'left_wheel_speed: {left_wheel_speed:2f}')

                # robot_pose_observation = None
                # if self._aruco.detect(self._camera.get_frame()):
                #     robot_pose_observation = self._aruco.get_camera_pose()

                v_rx = (right_wheel_speed + left_wheel_speed) / 2.0
                # v_ry = 0  # cannot move in y
                omega_r = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation  # in rad/s

                u_k[0, 0] = v_rx
                u_k[1, 0] = omega_r

                z_k = None
                self._frame = self._camera.get_frame()
                if self._aruco.detect(self._frame):
                    self._aruco.draw_markers(self._frame)
                    self._aruco.draw_axis(self._frame)

                    marker_poses = self._aruco.get_marker_poses()
                    min_marker_distance = None
                    min_marker_key = None
                    for key, value in marker_poses.items():
                        marker_tvec = value[0:3, 3:4]
                        marker_distance = np.sqrt(np.sum(marker_tvec ** 2))
                        if min_marker_distance is None:
                            min_marker_distance = marker_distance
                            min_marker_key = key
                        if marker_distance < min_marker_distance:
                            min_marker_distance = marker_distance
                            min_marker_key = key

                    # take marker that is closest to get an observation
                    marker_pose = marker_poses[min_marker_key]

                    # take the inverse to get the camera position (marker is at world 0, 0)
                    camera_pose = np.linalg.inv(marker_pose)

                    rotation_matrix = camera_pose[0:3, 0:3]

                    # x and y axis are not the same for markers as the robot coordinate frame
                    # need to rotate 90 degrees in z to match

                    # rotation_matrix_90 = np.array([0, -1, 0],
                    #                               [1, 0, 0],
                    #                               [0, 0, 1])

                    if isRotationMatrix(rotation_matrix):
                        euler_angles = rotationMatrixToEulerAngles(rotation_matrix)
                        # only need yaw (z)
                        yaw = euler_angles[2]
                        # print(f'yaw: {math.degrees(yaw):.2f}')
                        # print(f'x: {camera_pose[0, 3]} | y: {camera_pose[1, 3]}')
                        # z_k = np.array([[camera_pose[2, 3]], [-camera_pose[0, 3]], [yaw + math.pi/2.0]])
                        z_k = np.array([[camera_pose[0, 3]], [camera_pose[1, 3]], [yaw]])

                # z_k = None
                self._ekf.update(u_k, z_k, dt)

                pose_mean = self._ekf.pose_mean
                pose_covariance = self._ekf.pose_covariance

                det = np.linalg.det(pose_covariance)

                # print(f'x: {pose_mean[0, 0]:.2f} | y: {pose_mean[1, 0]:.2f} | angle: {math.degrees(pose_mean[2, 0]):.2f}', end="\r")
                # print(f'det: {det:2f}')
                cv2.imshow("Image", self._frame)
                cv2.waitKey(1)



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

    @property
    def robot_view(self):
        return self._frame
