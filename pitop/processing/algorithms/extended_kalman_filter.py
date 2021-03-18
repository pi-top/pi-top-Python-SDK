"""
Extended kalman filter (EKF) localization sample
author: Atsushi Sakai (@Atsushi_twi)
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import time

# Estimation parameter of EKF
Q = np.diag([0.01, 0.01])**2  # predict state covariance
R = np.diag([0.1, 0.1, np.deg2rad(2.0)])**2  # Observation x, y position covariance


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
            z_pred = self.__observation_model()
            # print(f'z_pred: {z_pred}')
            y = z - z_pred
            # print(f'y: {y}')
            S = self._jH.dot(P_pred).dot(self._jH.T) + R
            K = P_pred.dot(self._jH.T).dot(np.linalg.inv(S))
            self._x_est = x_pred + K.dot(y)
            self._P_est = (np.eye(len(self._x_est)) - K.dot(self._jH)).dot(P_pred)
        else:
            self._x_est = x_pred
            self._P_est = P_pred



        # store historical data
        # self._hxEst = np.hstack((self._hxEst, self._x_est))
        #
        # plot(self._hxEst, self._x_est, self._P_est)

    # def __ekf_estimation(self, u, z, dt):
    #     #  Predict
    #     x_pred = self.__motion_model(u, dt)
    #     jF = self.jacobF(x_pred, u, dt)
    #     PPred = jF.dot(self._P_est).dot(jF.T) + R
    #
    #     #  Update
    #     if z is not None:
    #         zPred = self.observation_model(x_pred)
    #         y = z.T - zPred
    #         S = self._jH.dot(PPred).dot(self._jH.T) + Q
    #         K = PPred.dot(self._jH.T).dot(np.linalg.inv(S))
    #         self._x_est = x_pred + K.dot(y)
    #         self._P_est = (np.eye(len(self._x_est)) - K.dot(self._jH)).dot(PPred)
    #     else:
    #         self._x_est = x_pred
    #         # self._P_est =

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

        B = np.array([[dt * math.cos(theta_k), 0],
                      [dt * math.sin(theta_k), 0],
                      [0, dt]])

        x_pred = F.dot(self._x_est) + B.dot(u)

        return x_pred

    def __jacobF(self, u, dt):
        """
        Jacobian of Motion Model
        motion model
        x_{t+1} = x_t+v*dt*cos(yaw)
        y_{t+1} = y_t+v*dt*sin(yaw)
        yaw_{t+1} = yaw_t+omega*dt
        so
        dx/dyaw = -v*dt*sin(yaw)
        dy/dyaw = v*dt*cos(yaw)
        """
        theta_k = self._x_est[2, 0]
        v = u[0, 0]
        jF = np.array([[1.0, 0.0, -v * dt * math.sin(theta_k)],
                       [0.0, 1.0, v * dt * math.cos(theta_k)],
                       [0.0, 0.0, 1.0]])

        return jF

    def __jacobG(self, dt):
        theta_k = self._x_est[2, 0]
        jG = np.array([[dt * math.cos(theta_k), 0],
                       [dt * math.sin(theta_k), 0],
                       [0, dt]])

        return jG

    def __observation_model(self):
        #  Observation Model
        # This would need to account for camera position if not in a 2D map or if using pan mechanism
        H = np.array([[1.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0],
                      [0.0, 0.0, 1.0]])

        z = H.dot(self._x_est)

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