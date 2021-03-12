"""
Extended kalman filter (EKF) localization sample
author: Atsushi Sakai (@Atsushi_twi)
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import time

# Estimation parameter of EKF
Q = np.diag([1.0, 1.0])**2  # Observation x,y position covariance
R = np.diag([0.1, 0.1, np.deg2rad(1.0), 1.0])**2  # predict state covariance


class EKF:
    def __init__(self):
        # State Vector [x y yaw v]
        self._previous_time = time.time()
        self._x_est = np.zeros((4, 1))
        self._P_est = np.eye(4)
        self._xDR = np.zeros((4, 1))

        self._jH = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        # store data history
        self._hxEst = self._x_est
        self._hz = np.zeros((1, 2))

    def update(self, u, z):
        """
        :param u: Control vector [v, yaw_rate]
        :param z: Pose observation [x, y] TODO: will add theta later
        :return:
        """
        # predict
        current_time = time.time()
        dt = current_time - self._previous_time
        self.__ekf_estimation(u, z, dt)

        # store historical data
        self._hxEst = np.hstack((self._hxEst, self._x_est))

        plot(self._hxEst, self._x_est, self._P_est)

    def __ekf_estimation(self, u, z, dt):
        #  Predict
        x_pred = self.__motion_model(u, dt)
        jF = self.jacobF(x_pred, u, dt)
        PPred = jF.dot(self._P_est).dot(jF.T) + R

        #  Update
        zPred = self.observation_model(x_pred)
        y = z.T - zPred
        S = self._jH.dot(PPred).dot(self._jH.T) + Q
        K = PPred.dot(self._jH.T).dot(np.linalg.inv(S))
        self._x_est = x_pred + K.dot(y)
        self._P_est = (np.eye(len(self._x_est)) - K.dot(self._jH)).dot(PPred)

    def __motion_model(self, u, dt):
        F = np.array([[1.0, 0, 0, 0],
                      [0, 1.0, 0, 0],
                      [0, 0, 1.0, 0],
                      [0, 0, 0, 0]])

        B = np.array([[dt * math.cos(self._x_est[2, 0]), 0],
                      [dt * math.sin(self._x_est[2, 0]), 0],
                      [0.0, dt],
                      [1.0, 0.0]])

        x = F.dot(self._x_est) + B.dot(u)

        return x

    def jacobF(self, x, u, dt):
        """
        Jacobian of Motion Model
        motion model
        x_{t+1} = x_t+v*dt*cos(yaw)
        y_{t+1} = y_t+v*dt*sin(yaw)
        yaw_{t+1} = yaw_t+omega*dt
        v_{t+1} = v{t}
        so
        dx/dyaw = -v*dt*sin(yaw)
        dx/dv = dt*cos(yaw)
        dy/dyaw = v*dt*cos(yaw)
        dy/dv = dt*sin(yaw)
        """
        yaw = x[2, 0]
        v = u[0, 0]
        jF = np.array([
            [1.0, 0.0, -dt * v * math.sin(yaw), dt * math.cos(yaw)],
            [0.0, 1.0, dt * v * math.cos(yaw), dt * math.sin(yaw)],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]])

        return jF

    @staticmethod
    def observation_model(x):
        #  Observation Model
        H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        z = H.dot(x)

        return z


def plot(hxEst, x_est, P_est):
    plt.cla()
    plt.plot(hxEst[0, :].flatten(),
             hxEst[1, :].flatten(), "-r")
    plot_covariance_ellipse(x_est, P_est)
    plt.axis("equal")
    plt.grid(True)
    plt.pause(0.001)


def plot_covariance_ellipse(xEst, PEst):
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
    angle = math.atan2(eigvec[bigind, 1], eigvec[bigind, 0])
    R = np.array([[math.cos(angle), math.sin(angle)],
                  [-math.sin(angle), math.cos(angle)]])
    fx = R.dot(np.array([[x, y]]))
    px = np.array(fx[0, :] + xEst[0, 0]).flatten()
    py = np.array(fx[1, :] + xEst[1, 0]).flatten()
    plt.plot(px, py, "--r")


# def main():
#     print(__file__ + " start!!")
#
#     time = 0.0
#
#     # State Vector [x y yaw v]'
#     xEst = np.zeros((4, 1))
#     xTrue = np.zeros((4, 1))
#     PEst = np.eye(4)
#
#     xDR = np.zeros((4, 1))  # Dead reckoning
#
#     # history
#     hxEst = xEst
#     hxTrue = xTrue
#     hxDR = xTrue
#     hz = np.zeros((1, 2))
#
#     while SIM_TIME >= time:
#         time += DT
#         u = calc_input()
#
#         xTrue, z, xDR, ud = observation(xTrue, xDR, u)
#
#         xEst, PEst = ekf_estimation(xEst, PEst, z, ud)
#
#         # store data history
#         hxEst = np.hstack((hxEst, xEst))
#         hxDR = np.hstack((hxDR, xDR))
#         hxTrue = np.hstack((hxTrue, xTrue))
#         hz = np.vstack((hz, z))
#
#         if show_animation:
#             plt.cla()
#             plt.plot(hz[:, 0], hz[:, 1], ".g")
#             plt.plot(hxTrue[0, :].flatten(),
#                      hxTrue[1, :].flatten(), "-b")
#             plt.plot(hxDR[0, :].flatten(),
#                      hxDR[1, :].flatten(), "-k")
#             plt.plot(hxEst[0, :].flatten(),
#                      hxEst[1, :].flatten(), "-r")
#             plot_covariance_ellipse(xEst, PEst)
#             plt.axis("equal")
#             plt.grid(True)
#             plt.pause(0.001)
#
#
# if __name__ == '__main__':
#     main()