from threading import Thread, Event
from time import time
from dataclasses import dataclass
import numpy as np
from random import random
import math
from typing import Union
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


class GoalCriteria:
    def __init__(self, linear_speed_factor, angular_speed_factor):
        self._MAX_GOAL_REACHED_DISTANCE_ERROR = linear_speed_factor * 0.02  # 2 mm at full speed
        self._MAX_GOAL_REACHED_ANGLE_ERROR = angular_speed_factor * math.radians(4.0)  # 4deg at full speed

    def angle(self, angle_error):
        if abs(angle_error) < self._MAX_GOAL_REACHED_ANGLE_ERROR:
            return True
        return False

    def distance(self, distance_error, heading_error):
        if abs(distance_error) < self._MAX_GOAL_REACHED_DISTANCE_ERROR:
            return True
        if abs(heading_error) > math.pi / 2:
            # Overshot goal, error will be small so consider goal to be reached.
            # Otherwise robot would have to reverse a tiny amount which would be poor UX.
            # Robot will correct itself on subsequent navigation calls anyway.
            return True
        return False


class RobotDrivingParameters:
    def __init__(self, linear_speed_factor, angular_speed_factor, max_motor_speed, max_angular_speed):
        self.linear_speed_factor = linear_speed_factor
        self.angular_speed_factor = angular_speed_factor
        self._max_motor_speed = max_motor_speed
        self._max_angular_speed = max_angular_speed

        self.max_v = 0.0
        self.max_w = 0.0
        self.deceleration_distance = 0.0
        self.deceleration_angle = 0.0

        self.update_linear_speed(speed_factor=linear_speed_factor)
        self.update_angular_speed(speed_factor=angular_speed_factor)

    def update_linear_speed(self, speed_factor):
        self.max_v = speed_factor * self._max_motor_speed
        self.deceleration_distance = speed_factor * 0.4  # 0.4m at full speed

    def update_angular_speed(self, speed_factor):
        self.max_w = speed_factor * self._max_angular_speed
        self.deceleration_angle = speed_factor * math.radians(120.0)  # 120deg at full speed


class PIDManger:
    def __init__(self, deceleration_angle, deceleration_distance):
        self.heading = PID(Kp=1.0 / deceleration_angle,
                           Ki=0.1,
                           Kd=0.1,
                           setpoint=0.0,
                           output_limits=(-1.0, 1.0)
                           )
        self.distance = PID(Kp=1.0 / deceleration_distance,
                            Ki=0.1,
                            Kd=0.1,
                            setpoint=0.0,
                            output_limits=(-1.0, 1.0)
                            )

    def reset(self):
        self.heading.reset()
        self.distance.reset()


class NavigationController:
    def __init__(self,
                 drive_controller=None,
                 linear_speed_factor: float = 0.75,
                 angular_speed_factor: float = 0.5,
                 sim=False):

        self._robot_state = RobotState()
        self._odom_update_frequency = 10.0
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()

        self._sim = sim
        if not self._sim:
            self._drive_controller = drive_controller
            self._drive_params = RobotDrivingParameters(
                linear_speed_factor=linear_speed_factor,
                angular_speed_factor=angular_speed_factor,
                max_motor_speed=self._drive_controller.max_motor_speed,
                max_angular_speed=self._drive_controller.max_robot_angular_speed
            )
            self._goal_criteria = GoalCriteria(linear_speed_factor=linear_speed_factor,
                                               angular_speed_factor=angular_speed_factor
                                               )

        self._pid = PIDManger(deceleration_angle=self._drive_params.deceleration_angle,
                              deceleration_distance=self._drive_params.deceleration_distance
                              )

    def go_to(self, position: Union[tuple, None] = None, angle: Union[float, None] = None):

        if position is not None:
            x, y = position
            self.__set_course_heading(x_goal=x, y_goal=y)
            self.__drive_to_goal(x_goal=x, y_goal=y)

        if angle is not None:
            self.__rotate_to_theta_goal(theta_goal=math.radians(angle))

    @property
    def linear_speed_factor(self):
        return self._drive_params.linear_speed_factor

    @linear_speed_factor.setter
    def linear_speed_factor(self, speed_factor):
        self._drive_params.update_linear_speed(speed_factor)

    @property
    def angular_speed_factor(self):
        return self._drive_params.angular_speed_factor

    @angular_speed_factor.setter
    def angular_speed_factor(self, speed_factor):
        self._drive_params.update_angular_speed(speed_factor)

    def __set_course_heading(self, x_goal, y_goal):
        while True:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__normalize_angle(theta - math.atan2(y_diff, x_diff))
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if self._goal_criteria.angle(heading_error):
                self.__goal_reached()
                break

            self.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __drive_to_goal(self, x_goal, y_goal):
        while True:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__get_angle_error(current_angle=theta, target_angle=math.atan2(y_diff, x_diff))
            distance_error = -np.hypot(x_diff, y_diff)
            if self._goal_criteria.distance(distance_error=distance_error, heading_error=heading_error):
                self.__goal_reached()
                break

            angular_speed = self.__get_angular_speed(heading_error=heading_error)
            linear_speed = self.__get_linear_speed(distance_error=distance_error)

            self.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    def __rotate_to_theta_goal(self, theta_goal):
        while True:
            x, y, theta = self.__get_new_pose_update()

            heading_error = self.__get_angle_error(current_angle=theta, target_angle=theta_goal)
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if self._goal_criteria.angle(heading_error):
                self.__goal_reached()
                break

            self.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __goal_reached(self):
        self.stop()
        self._pid.reset()
        # wait for one more pose update before returning to ensure subsequent code has latest (could be user code)
        self._position_update_event.wait()
        self._position_update_event.clear()

    def __get_new_pose_update(self):
        self._position_update_event.wait()
        self._position_update_event.clear()
        return self._robot_state.pose

    def __get_angle_error(self, current_angle, target_angle):
        return self.__normalize_angle(current_angle - target_angle)

    @staticmethod
    def __normalize_angle(angle):
        """
        Converts to range -pi to +pi to prevent unstable behaviour when going from 0 to 2*pi with slight turn
        :param angle:
        :return: angle normalized to range -pi to +pi
        """
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def __get_angular_speed(self, heading_error):
        return self._drive_params.max_w * self._pid.heading(heading_error)

    def __get_linear_speed(self, distance_error):
        return self._drive_params.max_v * self._pid.distance(distance_error)

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

    def stop(self):
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
