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

    @property
    def pose(self):
        return self.x, self.y, self.theta

    def reset_pose(self):
        self.x, self.y, self.theta = (0.0, 0.0, 0.0)

    def calc_distance(self, point_x, point_y):
        dx = self.x - point_x
        dy = self.y - point_y
        return math.hypot(dx, dy)


class NavigationController:
    _DECELERATION_DISTANCE = 0.2
    _DECELERATION_ANGLE = math.radians(30.0)

    def __init__(self, drive_controller=None,
                 linear_speed_factor: float = 0.5,
                 angular_speed_factor: float = 0.25,
                 sim=False):

        self._sim = sim
        if not self._sim:
            self._drive_controller = drive_controller
            self._max_motor_speed = self._drive_controller.max_motor_speed
            self._max_robot_angular_speed = self._drive_controller.max_robot_angular_speed
            self._linear_speed_factor = linear_speed_factor
            self._angular_speed_factor = angular_speed_factor
            self._max_linear_speed = self._linear_speed_factor * self._max_motor_speed
            self._max_angular_speed = self._angular_speed_factor * self._max_robot_angular_speed

        self._odom_update_frequency = 10.0
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()
        self._robot_state = RobotState()

        self._heading_pid = PID(Kp=1.0 / self._DECELERATION_ANGLE,
                                Ki=0.1,
                                Kd=0.1,
                                setpoint=0.0,
                                output_limits=(-1.0, 1.0)
                                )
        self._position_pid = PID(Kp=1.0 / self._DECELERATION_DISTANCE,
                                 Ki=0.1,
                                 Kd=0.1,
                                 setpoint=0.0,
                                 output_limits=(-1.0, 1.0)
                                 )

    def go_to(self, x_goal: float, y_goal: float, theta_goal=None):

        if x_goal is not None and y_goal is not None:
            self.__set_course_heading(x_goal=x_goal, y_goal=y_goal)
            self.__drive_to_goal(x_goal=x_goal, y_goal=y_goal)
        if theta_goal is not None:
            self.__rotate_to_theta_goal(theta_goal=theta_goal)

    def __set_course_heading(self, x_goal, y_goal):
        while True:
            self._position_update_event.wait()
            self._position_update_event.clear()
            x, y, theta = self._robot_state.pose

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__normalize_angle(theta - math.atan2(y_diff, x_diff))
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if abs(heading_error) < np.radians(1.0):  # and abs(angular_speed < 0.1):
                print("Heading goal reached")
                self.__goal_reached()
                break

            self.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __drive_to_goal(self, x_goal, y_goal):

        while True:
            self._position_update_event.wait()
            self._position_update_event.clear()
            x, y, theta = self._robot_state.pose

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__normalize_angle(theta - math.atan2(y_diff, x_diff))
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            distance_error = -np.hypot(x_diff, y_diff)
            linear_speed = self.__get_linear_speed(distance_error=distance_error)

            if abs(distance_error) < 0.01:
                print("Position goal reached")
                self.__goal_reached()
                break

            self.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    def __rotate_to_theta_goal(self, theta_goal):
        while True:
            self._position_update_event.wait()
            self._position_update_event.clear()

            theta = self._robot_state.theta
            heading_error = self.__normalize_angle(theta - theta_goal)
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if abs(heading_error) < np.radians(1.0):  # and abs(angular_speed < 0.1):
                print("Theta goal reached")
                self.__goal_reached()
                break

            self.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __goal_reached(self):
        self.robot_stop()
        self._heading_pid.reset()
        self._position_update_event.wait()
        self._position_update_event.clear()

    @staticmethod
    def __normalize_angle(angle):
        """
        Converts to range -pi to +pi to prevent unstable behaviour when going from 0 to 2*pi with slight turn
        :param angle:
        :return: angle normalized to range -pi to +pi
        """
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def __get_angular_speed(self, heading_error):
        return self._max_angular_speed * self._heading_pid(heading_error)

    def __get_linear_speed(self, distance_error):
        return self._max_linear_speed * self._position_pid(distance_error)

    def __track_odometry(self):

        prev_time = time()
        while True:
            current_time = time()
            dt = current_time - prev_time
            if dt < 1.0 / self._odom_update_frequency:
                continue
            prev_time = current_time
            self.__update_state(dt)
            self._position_update_event.set()

    def __update_state(self, dt):
        if not self._sim:
            left_wheel_speed = self._drive_controller.left_motor.current_speed
            right_wheel_speed = self._drive_controller.right_motor.current_speed

            self._robot_state.v = (right_wheel_speed + left_wheel_speed) / 2.0
            self._robot_state.w = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation

        self._robot_state.x = self._robot_state.x + self._robot_state.v * np.cos(self._robot_state.theta) * dt
        self._robot_state.y = self._robot_state.y + self._robot_state.v * np.sin(self._robot_state.theta) * dt
        self._robot_state.theta = self.__normalize_angle(self._robot_state.theta + self._robot_state.w * dt)

    def reset_position(self):
        self._robot_state.reset_pose()

    def robot_stop(self):
        if self._sim:
            self._robot_state.v = 0.0
            self._robot_state.w = 0.0
        else:
            self._drive_controller.stop()

    def robot_move(self, linear_speed, angular_speed):
        if self._sim:
            self._robot_state.v = linear_speed
            self._robot_state.w = angular_speed
        else:
            self._drive_controller.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)


if __name__ == "__main__":
    nav_controller = NavigationController(sim=True)
    x_start = 20 * random()
    y_start = 20 * random()
    theta_start = 0  # 2 * math.pi * random() - math.pi
    nav_controller._robot_state.x = x_start
    nav_controller._robot_state.y = y_start
    nav_controller._robot_state.theta = theta_start

    x_target = 5  # 20 * random()
    y_target = 10  # 20 * random()
    theta_target = 2 * math.pi * random() - math.pi

    nav_controller.go_to(x_target, y_target, theta_target)
    print("finished")
