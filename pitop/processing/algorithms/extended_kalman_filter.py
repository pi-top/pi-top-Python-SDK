"""
Extended kalman filter (EKF) localization sample
author: Atsushi Sakai (@Atsushi_twi)
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import time


# Estimation parameter of EKF
Q = np.diag([0.05, 0.05])**2  # predict state covariance (v, omega)
R = np.diag([0.1, 0.1, np.deg2rad(1.0)])**2  # Observation position covariance (x, y, yaw)


def plot_covariance_ellipse(xEst, PEst):  # pragma: no cover
    Pxy = PEst[0:2, 0:2]
    eigval, eigvec = np.linalg.eig(Pxy)

    if eigval[0] >= eigval[1]:
        bigind = 0
        smallind = 1
    else:
        bigind = 1
        smallind = 0

    t = np.arange(0, 2 * math.pi + 0.1, 0.1)
    a = math.sqrt(eigval[bigind])
    b = math.sqrt(eigval[smallind])
    x = [a * math.cos(it) for it in t]
    y = [b * math.sin(it) for it in t]
    angle = math.atan2(eigvec[1, bigind], eigvec[0, bigind])
    # rot = Rot.from_euler('z', angle).as_matrix()[0:2, 0:2]
    fx = (np.array([x, y]))
    px = np.array(fx[0, :] + xEst[0, 0]).flatten()
    py = np.array(fx[1, :] + xEst[1, 0]).flatten()
    plt.plot(px, py, "--r")


class EKF:
    def __init__(self):
        # State Vector [x y yaw]
        self._previous_time = time.time()
        self._x_est = np.zeros((3, 1))
        self._P_est = np.eye(3)
        self._x_dead_reckoning = np.zeros((3, 1))

        self._jH = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        #
        # store data history
        self._hxEst = self._x_est
        self._hz = np.zeros((1, 2))

    def update(self, u, z, dt):
        """
        :param u: Control vector [v, yaw_rate] from odometry
        :param z: Pose observation [x, y, yaw] 
        :return:
        """
        x_pred = self.__motion_model(u, dt)

        self._x_dead_reckoning = np.hstack((self._x_dead_reckoning, x_pred))

        jF = self.__jacobF(u, dt)

        jG = self.__jacobG(dt)

        P_pred = jF.dot(self._P_est).dot(jF.T) + jG.dot(Q).dot(jG.T)

        #  Update based on observation if available
        if z is not None:
            # print(f'z: {z}')
            z_pred = self.__observation_model(x_pred)
            # print(f'z_pred: {z_pred}')
            y = z - z_pred
            print(f'y: {y}')
            # S = self._jH.dot(P_pred).dot(self._jH.T) + R
            # K = P_pred.dot(self._jH.T).dot(np.linalg.inv(S))
            # self._x_est = x_pred + K.dot(y)
            # self._P_est = (np.eye(len(self._x_est)) - K.dot(self._jH)).dot(P_pred)

            S = P_pred + R
            K = P_pred.dot(np.linalg.inv(S))
            self._x_est = x_pred + K.dot(y)
            self._P_est = (np.eye(len(self._x_est)) - K).dot(P_pred)
        else:
            self._x_est = x_pred
            self._P_est = P_pred

        # make sure between 0 and 360
        # self._x_est[2, 0]
        # store historical data
        self._hxEst = np.hstack((self._hxEst, self._x_est))

        plt.cla()
        # for stopping simulation with the esc key.
        # plt.gcf().canvas.mpl_connect('key_release_event',
        #                              lambda event: [exit(0) if event.key == 'escape' else None])

        # plt.plot(self._x_dead_reckoning[0, :].flatten(),
        #          self._x_dead_reckoning[1, :].flatten(), "-k")
        plt.plot(self._hxEst[0, :].flatten(),
                 self._hxEst[1, :].flatten(), "-r")
        plot_covariance_ellipse(self._x_est, self._P_est)
        plt.axis("equal")
        plt.grid(True)
        plt.pause(0.001)

    @property
    def pose_mean(self):
        return self._x_est

    @property
    def pose_covariance(self):
        return self._P_est

    def __motion_model(self, u, dt):
        F = np.array([[1.0, 0, 0],
                      [0, 1.0, 0],
                      [0, 0, 1.0]])

        theta_k = self._x_est[2, 0]

        B = np.array([[-dt * math.sin(theta_k), 0],
                      [dt * math.cos(theta_k), 0],
                      [0, dt]])

        x_pred = F.dot(self._x_est) + B.dot(u)

        # convert to world frame reference

        return x_pred

    def __jacobF(self, u, dt):
        """
        Jacobian of Motion Model motion model with respect to state vector
        x_{t+1} = x_t - v*dt*sin(yaw)
        y_{t+1} = y_t + v*dt*cos(yaw)
        yaw_{t+1} = yaw_t + omega*dt
        so
        dx/dyaw = -v*dt*cos(yaw)
        dy/dyaw = -v*dt*sin(yaw)
        """
        theta_k = self._x_est[2, 0]
        v = u[0, 0]
        jF = np.array([[1.0, 0.0, -v * dt * math.cos(theta_k)],
                       [0.0, 1.0, -v * dt * math.sin(theta_k)],
                       [0.0, 0.0, 1.0]])

        return jF

    def __jacobG(self, dt):
        """
        Jacobian of motion model with respect to the input vector
        x_{t+1} = x_t - v*dt*sin(yaw)
        y_{t+1} = y_t + v*dt*cos(yaw)
        yaw_{t+1} = yaw_t + omega*dt
        so:
        dx/dv = -dt*sin(yaw)
        dy/dv = dt*cos(yaw)
        d(yaw)/d(omega) = dt
        :param dt:
        :return:
        """
        theta_k = self._x_est[2, 0]
        jG = np.array([[-dt * math.sin(theta_k), 0],
                       [dt * math.cos(theta_k), 0],
                       [0, dt]])

        return jG

    @staticmethod
    def __observation_model(x_pred):
        #  Observation Model
        # This would need to account for camera position if not in a 2D map or if using pan mechanism
        H = np.array([[1.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0],
                      [0.0, 0.0, 1.0]])

        z = H.dot(x_pred)

        return z


def plot(hxEst, x_est, P_est):
    plt.cla()
    plt.plot(hxEst[0, :].flatten(),
             hxEst[1, :].flatten(), "-r")
    plot_covariance_ellipse(x_est, P_est)
    plt.axis("equal")
    plt.grid(True)
    plt.pause(0.001)
