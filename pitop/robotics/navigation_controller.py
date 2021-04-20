from threading import Thread, Event
from time import time
from dataclasses import dataclass
import numpy as np


@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    v: float = 0.0
    w: float = 0.0


class NavigationController:
    def __init__(self, drive_controller=None):
        # self._drive_controller = drive_controller
        # self._left_motor = drive_controller.left_motor
        # self._right_motor = drive_controller.right_motor
        self._current_position = (0.0, 0.0)
        self._odom_update_frequency = 5.0
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()
        self._robot_state = RobotState()
        self._kp_rho = 9
        self._kp_alpha = 15
        self._kp_beta = -3

    def go_to(self, x_goal, y_goal, theta_goal):
        x = self._robot_state.x
        y = self._robot_state.y

        x_diff = x_goal - x
        y_diff = y_goal - y

        rho = np.hypot(x_diff, y_diff)
        while rho > 0.001:
            x = self._robot_state.x
            y = self._robot_state.y
            theta = self._robot_state.theta

            x_diff = x_goal - x
            y_diff = y_goal - y

            # Restrict alpha and beta (angle differences) to the range
            # [-pi, pi] to prevent unstable behavior e.g. difference going
            # from 0 rad to 2*pi rad with slight turn

            rho = np.hypot(x_diff, y_diff)
            print(f"rho: {rho}")

            alpha = (np.arctan2(y_diff, x_diff) - theta + np.pi) % (2 * np.pi) - np.pi
            beta = (theta_goal - theta - alpha + np.pi) % (2 * np.pi) - np.pi

            v = self._kp_rho * rho
            w = self._kp_alpha * alpha + self._kp_beta * beta

            if alpha > np.pi / 2 or alpha < -np.pi / 2:
                v = -v

            self._robot_state.v = v
            self._robot_state.w = w

            self._position_update_event.wait()
            self._position_update_event.clear()

    def __track_odometry(self):

        prev_time = time()
        while True:
            current_time = time()
            dt = current_time - prev_time
            if dt < 1.0 / self._odom_update_frequency:
                continue
            prev_time = current_time
            self._robot_state.x += self._robot_state.v * np.cos(self._robot_state.theta) * dt
            self._robot_state.y += self._robot_state.v * np.sin(self._robot_state.theta) * dt
            self._robot_state.theta += self._robot_state.w * dt
            print(self._robot_state)
            self._position_update_event.set()

    def reset_position(self):
        self._current_position = (0.0, 0.0)


if __name__ == "__main__":
    nav_controller = NavigationController()
    nav_controller.go_to(10, 10, np.pi)
    print("finished")
