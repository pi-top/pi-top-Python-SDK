from threading import Thread, Event
from time import time
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from random import random
import math
from simple_pid import PID


@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    v: float = 0.0
    w: float = 0.0

    def calc_distance(self, point_x, point_y):
        dx = self.x - point_x
        dy = self.y - point_y
        return math.hypot(dx, dy)


k = 0.1  # look forward gain
Lfc = 2.0  # [m] look-ahead distance
Kp = 1.0  # speed proportional gain
dt = 0.1  # [s] time tick
WB = 2.9  # [m] wheel base of vehicle


class TargetCourse:

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.old_nearest_point_index = None

    def search_target_index(self, state):

        # To speed up nearest point search, doing it at only first time.
        if self.old_nearest_point_index is None:
            # search nearest point index
            dx = [state.rear_x - icx for icx in self.cx]
            dy = [state.rear_y - icy for icy in self.cy]
            d = np.hypot(dx, dy)
            ind = np.argmin(d)
            self.old_nearest_point_index = ind
        else:
            ind = self.old_nearest_point_index
            distance_this_index = state.calc_distance(self.cx[ind],
                                                      self.cy[ind])
            while True:
                distance_next_index = state.calc_distance(self.cx[ind + 1],
                                                          self.cy[ind + 1])
                if distance_this_index < distance_next_index:
                    break
                ind = ind + 1 if (ind + 1) < len(self.cx) else ind
                distance_this_index = distance_next_index
            self.old_nearest_point_index = ind

        Lf = k * state.v + Lfc  # update look ahead distance

        # search look ahead target point index
        while Lf > state.calc_distance(self.cx[ind], self.cy[ind]):
            if (ind + 1) >= len(self.cx):
                break  # not exceed goal
            ind += 1

        return ind, Lf


class NavigationController:
    def __init__(self, drive_controller=None):
        # self._drive_controller = drive_controller
        # self._left_motor = drive_controller.left_motor
        # self._right_motor = drive_controller.right_motor
        self._current_position = (0.0, 0.0)
        self._odom_update_frequency = 10.0
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()
        self._robot_state = RobotState()
        self._heading_pid = PID(Kp=0.5,
                                Ki=0.001,
                                Kd=0.001,
                                setpoint=0.0,
                                output_limits=(-2.0, 2.0)
                                )
        self._position_pid = PID(Kp=0.1,
                                 Ki=0.001,
                                 Kd=0.001,
                                 setpoint=0.0,
                                 output_limits=(-0.45, 0.45)
                                 )

    def go_to(self, x_goal, y_goal, theta_goal):
        self.__set_course_heading(x_goal, y_goal)
        self.__drive_to_goal(x_goal, y_goal)
        # self.__rotation_to_angle_goal()

    def __set_course_heading(self, x_goal, y_goal):

        while True:
            self._position_update_event.wait()
            self._position_update_event.clear()

            x = self._robot_state.x
            y = self._robot_state.y
            theta = self._robot_state.theta

            x_diff = x_goal - x
            y_diff = y_goal - y
            heading_error = theta - math.atan2(y_diff, x_diff)
            angular_speed = self._heading_pid(heading_error)
            print(heading_error)
            if abs(heading_error) < np.radians(1.0) and abs(angular_speed < 0.1):
                print("Heading goal reached")
                self._robot_state.w = 0
                self._heading_pid.reset()
                break

            self._robot_state.w = angular_speed

    def __drive_to_goal(self, x_goal, y_goal):

        while True:
            self._position_update_event.wait()
            self._position_update_event.clear()

            x = self._robot_state.x
            y = self._robot_state.y
            theta = self._robot_state.theta

            x_diff = x_goal - x
            y_diff = y_goal - y
            heading_error = theta - math.atan2(y_diff, x_diff)
            angular_speed = self._heading_pid(heading_error)
            self._robot_state.w = angular_speed

            distance_error = -np.hypot(x_diff, y_diff)
            print(distance_error)
            linear_speed = self._position_pid(distance_error)
            print(linear_speed)
            if distance_error < 0.1 and linear_speed < 0.05:
                print("Position goal reached")
                self._robot_state.v = 0
                self._robot_state.w = 0
                self._heading_pid.reset()
                break

            self._robot_state.v = linear_speed

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
            # print(self._robot_state)
            self._position_update_event.set()

    def reset_position(self):
        self._current_position = (0.0, 0.0)


def transformation_matrix(x, y, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), x],
        [np.sin(theta), np.cos(theta), y],
        [0, 0, 1]
    ])


def plot_vehicle(x, y, theta, x_traj, y_traj):  # pragma: no cover
    # Corners of triangular vehicle when pointing to the right (0 radians)
    p1_i = np.array([0.5, 0, 1]).T
    p2_i = np.array([-0.5, 0.25, 1]).T
    p3_i = np.array([-0.5, -0.25, 1]).T

    T = transformation_matrix(x, y, theta)
    p1 = np.matmul(T, p1_i)
    p2 = np.matmul(T, p2_i)
    p3 = np.matmul(T, p3_i)

    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-')
    plt.plot([p2[0], p3[0]], [p2[1], p3[1]], 'k-')
    plt.plot([p3[0], p1[0]], [p3[1], p1[1]], 'k-')

    plt.plot(x_traj, y_traj, 'b--')

    # for stopping simulation with the esc key.
    plt.gcf().canvas.mpl_connect('key_release_event',
                                 lambda event: [exit(0) if event.key == 'escape' else None])

    plt.xlim(0, 20)
    plt.ylim(0, 20)


if __name__ == "__main__":
    nav_controller = NavigationController()
    x_start = 20 * random()
    y_start = 20 * random()
    theta_start = 0  # 2 * np.pi * random() - np.pi
    nav_controller._robot_state.x = x_start
    nav_controller._robot_state.y = y_start
    nav_controller._robot_state.theta = theta_start

    x_goal = 5  # 20 * random()
    y_goal = 10  # 20 * random()
    theta_goal = 2 * np.pi * random() - np.pi

    nav_controller.go_to(x_goal, y_goal, theta_goal)
    print("finished")
