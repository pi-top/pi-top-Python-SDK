import numpy as np
import math
from filterpy.kalman import KalmanFilter
from enum import IntEnum
from .utils import normalize_angle
from collections import deque
from filterpy.common import Q_discrete_white_noise, Saver
import matplotlib.pyplot as plt


class State(IntEnum):
    x = 0
    y = 1
    theta = 2
    v = 3
    w = 4


class VelocityType(IntEnum):
    """Helper class to ensure v and w values are accessed at the correct
    position in various vectors and matrices."""
    v = 0
    w = 1


class VelocityMeasurements(IntEnum):
    previous = 0
    current = 1


class RobotStateFilter:
    _sigma_default_dt = 0.1

    def __init__(self, predict_frequency):
        self._kalman_filter = KalmanFilter(dim_x=len(State), dim_z=2, dim_u=2)
        self._saver = Saver(self._kalman_filter)
        self.u = None
        self._velocities = deque(maxlen=2)
        self._velocities.append(np.zeros((len(VelocityType), 1), dtype=float))  # [v, w].

        # Starting covariance is small since we know with high confidence we are starting at [0, 0, 0] with 0 velocity
        self._kalman_filter.P = np.eye(5) * 1e-6

        sigma = 0.001 / (self._sigma_default_dt * predict_frequency)
        acceleration_dt = 0.001 / (self._sigma_default_dt * predict_frequency)
        # the Q matrix is the covariance of the expected state change over the time interval dt
        # A rule of thumb for Q is to set it between  0.5Δ𝑎  to  Δ𝑎 , where  Δ𝑎  is the maximum amount that the
        # acceleration will change between sample periods.
        # If Q is large, we don't trust the Kalman predictions
        self._kalman_filter.Q = np.diag([sigma ** 2,
                                         sigma ** 2,
                                         math.radians(sigma),
                                         acceleration_dt ** 2,
                                         acceleration_dt ** 2]
                                        )

        # State transition function is the identity matrix
        self._kalman_filter.F = np.diag([1, 1, 1, 0, 0])

        # Measurement function H where z = Hx
        self._kalman_filter.H = np.array([[0, 0, 0, 1, 0],
                                          [0, 0, 0, 0, 1]
                                          ])

        # Velocity measurement uncertainty
        # If R is large, we don't trust the measurements (z)
        self._kalman_filter.R = np.array([[0.01 ** 2, 0.0],
                                          [0.0, 0.01 ** 2]
                                          ])

    def __str__(self):
        degree_symbol = u'\N{DEGREE SIGN}'
        return f"               x = {self.x:.3} m (+/- {self.x_tolerance:.3})\n" \
               f"               y = {self.y:.3} m (+/- {self.y_tolerance:.3})\n" \
               f"           Angle = {self.angle:.3}{degree_symbol} (+/- {self.angle_tolerance:.3})\n" \
               f"        Velocity = {self.v:.3} m/s (+/- {self.v_tolerance:.3})\n" \
               f"Angular velocity = {math.degrees(self.w):.3} {degree_symbol}/s " \
               f"(+/- {math.degrees(self.w_tolerance):.3})\n"

    def add_measurements(self, odom_measurements, dt, imu_measurements=None):
        self._velocities.append(odom_measurements)
        self.__kalman_predict(u=self._velocities[VelocityMeasurements.previous], dt=dt)
        self.__kalman_update(z=self._velocities[VelocityMeasurements.current], dt=dt)

    def __kalman_predict(self, u, dt):
        """
        Full predict equation is x1 = Fx0 + Bu0 where F is constant and defined in __init__
        B is the control transition matrix which is multiplied by u0 (control vector)
        B is derived from basic newtonian mechanics to predict new state from previous state information.

        Predict equations:
        x1 = x0 + dt * v0 * cos(theta + 0.5 * dt * w0)
        y1 = y0 + dt * v0 * sin(theta + 0.5 * dt * w0)
            (the 0.5 is a first order approximation to a curved path resulting from angular velocity w0)
        theta1 = dt * w0
        v1 = v0  # zero acceleration model, process noise Q allows for perturbations in velocity
        w1 = w0  # zero acceleration model, process noise Q allows for perturbations in velocity

        :param u: Control input vector
        :param dt: difference in time between measurements
        """
        B = np.array([[dt * math.cos(self.angle_rad + 0.5 * dt * self.w), 0],
                      [dt * math.sin(self.angle_rad + 0.5 * dt * self.w), 0],
                      [0., dt],
                      [1., 0.],
                      [0., 1.]]
                     )
        self._kalman_filter.predict(u=u, B=B)

    def __kalman_update(self, z):
        self._kalman_filter.update(z=z)

    @property
    def x(self):
        """
        :return float: Estimated x position of the robot in meters.
        """
        return self._kalman_filter.x[State.x, 0]

    @x.setter
    def x(self, value):
        self._kalman_filter.x[State.x, 0] = value

    @property
    def x_tolerance(self):
        """Returns the 2-sigma value for the variance in x.

        About 95% of the possible values for the true value of x lie
        within two standard deviations of the mean.
        :return: 2-sigma value of the x position
        """
        return 2 * np.sqrt(self._kalman_filter.P[State.x, State.x])

    @property
    def y(self):
        """
        :return float: Estimated y position of the robot in meters.
        """
        return self._kalman_filter.x[State.y, 0]

    @y.setter
    def y(self, value):
        self._kalman_filter.x[State.y, 0] = value

    @property
    def y_tolerance(self):
        """Returns the 2-sigma value for the variance in y.

        About 95% of the possible values for the true value of y lie
        within two standard deviations of the mean.
        :return: 2-sigma value of the y position
        """
        return 2 * np.sqrt(self._kalman_filter.P[State.y, State.y])

    @property
    def angle(self):
        """
        :return float: Estimated angle of the robot in degrees.
        """
        return math.degrees(self.angle_rad)

    @angle.setter
    def angle(self, value):
        self.angle_rad = math.radians(value)

    @property
    def angle_tolerance(self):
        """Returns the 2-sigma value for the variance in the angle.

        About 95% of the possible values for the true value of
        the angle lie within two standard deviations of the mean.
        :return: 2-sigma value of the angle position in degrees
        """
        return math.degrees(self.angle_rad_tolerance)

    @property
    def angle_rad(self):
        return self._kalman_filter.x[State.theta, 0]

    @angle_rad.setter
    def angle_rad(self, value):
        self._kalman_filter.x[State.theta, 0] = value

    @property
    def angle_rad_tolerance(self):
        """Returns the 2-sigma value for the variance in the angle.

        About 95% of the possible values for the true value of
        the angle lie within two standard deviations of the mean.
        :return: 2-sigma value of the angle position in radians
        """
        return 2 * np.sqrt(self._kalman_filter.P[State.theta, State.theta])

    @property
    def v(self):
        """
        :return float: Estimated linear velocity of the robot in meters/second.
        """
        return self._kalman_filter.x[State.v, 0]

    @property
    def v_tolerance(self):
        return 2 * np.sqrt(self._kalman_filter.P[State.v, State.v])

    @property
    def w(self):
        """
        :return float: Estimated angular velocity of the robot in radians/second.
        """
        return self._kalman_filter.x[State.w, 0]

    @property
    def w_tolerance(self):
        return 2 * np.sqrt(self._kalman_filter.P[State.w, State.w])

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
        self.x, self.y, self.angle_rad = (0, 0, 0)
