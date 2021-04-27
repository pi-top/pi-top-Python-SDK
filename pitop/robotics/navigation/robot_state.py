import numpy as np
import math
from filterpy.kalman import KalmanFilter
from enum import IntEnum
from .utils import normalize_angle


class PoseIndex(IntEnum):
    """
    Helper class to ensure x, y and theta values are accessed at the correct position in various vectors and matrices.
    """
    x = 0
    y = 1
    theta = 2


class VelocityIndex(IntEnum):
    """
    Helper class to ensure v and w values are accessed at the correct position in various vectors and matrices.
    """
    v = 0
    w = 1


class RobotState:
    _sigma_default_dt = 0.1

    def __init__(self, predict_frequency):
        self._kalman_filter = KalmanFilter(dim_x=len(PoseIndex), dim_z=3, dim_u=len(VelocityIndex))

        self._pose_estimate = np.zeros((len(PoseIndex), 1), dtype=float)  # [x, y theta].
        self._velocities = np.zeros((len(VelocityIndex), 1), dtype=float)  # [v, w].

        # Starting covariance is small since we know with high confidence we are starting at [0, 0, 0] (in a world of
        # pure dead-reckoning)
        self._sigma = 0.001 / (self._sigma_default_dt * predict_frequency)
        self._kalman_filter.P = np.array([[self._sigma ** 2, 0.0, 0.0],
                                          [0.0, self._sigma ** 2, 0.0],
                                          [0.0, 0.0, math.radians(self._sigma)]])

        # the Q matrix is the covariance of the expected state change over the time interval dt
        self._kalman_filter.Q = np.array([[self._sigma ** 2, 0.0, 0.0],
                                          [0.0, self._sigma ** 2, 0.0],
                                          [0.0, 0.0, math.radians(self._sigma)]])

    def __str__(self):
        degree_symbol = u'\N{DEGREE SIGN}'
        return f"               x = {self.x:.3} m (+/- {self.x_tolerance:.3})\n" \
               f"               y = {self.y:.3} m (+/- {self.y_tolerance:.3})\n" \
               f"           Angle = {self.angle:.3}{degree_symbol} (+/- {self.angle_tolerance:.3})\n" \
               f"        Velocity = {self.v:.3} m/s\n" \
               f"Angular velocity = {math.degrees(self.w):.3} {degree_symbol}/s\n" \


    def kalman_predict(self, u, dt):
        self._velocities = u
        B = np.array([[dt * math.cos(self.angle_rad), 0],
                      [dt * math.sin(self.angle_rad), 0],
                      [0, dt]]
                     )
        self._kalman_filter.predict(u=u, B=B)
        updated_pose = self._kalman_filter.x
        self.x = updated_pose[PoseIndex.x, 0]
        self.y = updated_pose[PoseIndex.y, 0]
        self.angle_rad = normalize_angle(updated_pose[PoseIndex.theta, 0])

    def kalman_update(self, z):
        self._kalman_filter.update(z=z)

    @property
    def x(self):
        """
        :return float: Estimated x position of the robot in meters.
        """
        return self._pose_estimate[PoseIndex.x, 0]

    @x.setter
    def x(self, value):
        self._pose_estimate[PoseIndex.x, 0] = value

    @property
    def x_tolerance(self):
        """
        Returns the 2-sigma value for the variance in x. About 95% of the possible values for the true value of x lie
        within two standard deviations of the mean.
        :return: 2-sigma value of the x position
        """
        return 2 * np.sqrt(self._kalman_filter.P[PoseIndex.x, PoseIndex.x])

    @property
    def y(self):
        """
        :return float: Estimated y position of the robot in meters.
        """
        return self._pose_estimate[PoseIndex.y, 0]

    @y.setter
    def y(self, value):
        self._pose_estimate[PoseIndex.y, 0] = value

    @property
    def y_tolerance(self):
        """
        Returns the 2-sigma value for the variance in y. About 95% of the possible values for the true value of y lie
        within two standard deviations of the mean.
        :return: 2-sigma value of the y position
        """
        return 2 * np.sqrt(self._kalman_filter.P[PoseIndex.y, PoseIndex.y])

    @property
    def angle(self):
        """
        :return float: Estimated angle of the robot in degrees.
        """
        return math.degrees(self._pose_estimate[PoseIndex.theta, 0])

    @angle.setter
    def angle(self, value):
        self._pose_estimate[PoseIndex.theta, 0] = math.radians(value)

    @property
    def angle_tolerance(self):
        """
        Returns the 2-sigma value for the variance in the angle. About 95% of the possible values for the true value of
        the angle lie within two standard deviations of the mean.
        :return: 2-sigma value of the angle position in degrees
        """
        return math.degrees(self.angle_rad_tolerance)

    @property
    def angle_rad(self):
        return self._pose_estimate[PoseIndex.theta, 0]

    @angle_rad.setter
    def angle_rad(self, value):
        self._pose_estimate[PoseIndex.theta, 0] = value

    @property
    def angle_rad_tolerance(self):
        """
        Returns the 2-sigma value for the variance in the angle. About 95% of the possible values for the true value of
        the angle lie within two standard deviations of the mean.
        :return: 2-sigma value of the angle position in radians
        """
        return 2 * np.sqrt(self._kalman_filter.P[PoseIndex.theta, PoseIndex.theta])

    @property
    def v(self):
        """
        :return float: Estimated linear velocity of the robot in meters/second.
        """
        return self._velocities[VelocityIndex.v, 0]

    @property
    def w(self):
        """
        :return float: Estimated angular velocity of the robot in radians/second.
        """
        return self._velocities[VelocityIndex.w, 0]

    @property
    def position(self):
        """
        :return: Estimated position of the robot as a tuple in the form (x, y) where x and y are in meters.
        """
        return self.x, self.y

    @position.setter
    def position(self, value: tuple):
        self.x, self.y = value

    def reset_pose(self):
        self._pose_estimate = np.zeros((3, 1), dtype=float)
