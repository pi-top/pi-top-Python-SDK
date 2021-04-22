from threading import Thread, Event
from time import time
from dataclasses import dataclass
import numpy as np
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
    def __init__(self, max_motor_speed, max_angular_speed):
        self._max_motor_speed = max_motor_speed
        self._max_angular_speed = max_angular_speed

        self.linear_speed_factor = 0.0
        self.angular_speed_factor = 0.0
        self.max_v = 0.0
        self.max_w = 0.0
        self.deceleration_distance = 0.0
        self.deceleration_angle = 0.0

    def update_linear_speed(self, speed_factor):
        self.linear_speed_factor = speed_factor
        self.max_v = self.linear_speed_factor * self._max_motor_speed
        self.deceleration_distance = self.linear_speed_factor * 0.4  # 0.4m at full speed

    def update_angular_speed(self, speed_factor):
        self.angular_speed_factor = speed_factor
        self.max_w = self.angular_speed_factor * self._max_angular_speed
        self.deceleration_angle = self.angular_speed_factor * math.radians(120.0)  # 120deg at full speed


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
    __VALID_ANGLE_RANGE = 180

    def __init__(self,
                 drive_controller=None,
                 linear_speed_factor: float = 0.75,
                 angular_speed_factor: float = 0.5
                 ):

        # callback to call once navigation complete
        self._on_finish = None

        # Navigation flow control
        self._navigation_in_progress = False
        self._stop_triggered = False
        self._nav_goal_finish_event = Event()
        self._nav_sub_goal_finish_event = Event()
        self._nav_thread = None
        self._sub_goal_nav_thread = None

        # Odometry tracking
        self._odom_update_frequency = 10.0
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()

        # Robot state and control
        self.robot_state = RobotState()
        self._drive_controller = drive_controller
        self._drive_params = RobotDrivingParameters(max_motor_speed=self._drive_controller.max_motor_speed,
                                                    max_angular_speed=self._drive_controller.max_robot_angular_speed
                                                    )
        self.linear_speed_factor = linear_speed_factor
        self.angular_speed_factor = angular_speed_factor
        self._goal_criteria = GoalCriteria(linear_speed_factor=linear_speed_factor,
                                           angular_speed_factor=angular_speed_factor
                                           )
        self._pid = PIDManger(deceleration_angle=self._drive_params.deceleration_angle,
                              deceleration_distance=self._drive_params.deceleration_distance
                              )

    def go_to(self, position: Union[list, None] = None, angle: Union[float, None] = None, on_finish=None):
        self._on_finish = on_finish

        if self._navigation_in_progress:
            raise RuntimeError("Cannot call function before previous navigation is complete, use .wait() or call "
                               ".stop() to cancel the previous navigation request.")

        if position is not None:
            if len(position) != 2 or type(position) is not list:
                raise ValueError("Position should be a list of size two in the form [x, y].")

        if angle is not None:
            if not (-self.__VALID_ANGLE_RANGE <= angle <= self.__VALID_ANGLE_RANGE):
                raise ValueError(f"Angle must from {-self.__VALID_ANGLE_RANGE} to {self.__VALID_ANGLE_RANGE}.")

        self._nav_thread = Thread(target=self.__navigate, args=(position, angle,), daemon=True).start()
        return self

    def __navigate(self, position, angle):
        self.__navigation_started()

        if position is not None:
            x, y = position
            self._sub_goal_nav_thread = Thread(target=self.__set_course_heading, args=(x, y,), daemon=True)
            self.__sub_goal_flow_control()
            self._sub_goal_nav_thread = Thread(target=self.__drive_to_position_goal, args=(x, y,), daemon=True)
            self.__sub_goal_flow_control()

        if angle is not None:
            self._sub_goal_nav_thread = Thread(target=self.__rotate_to_angle_goal, args=(angle,), daemon=True)
            self.__sub_goal_flow_control()

        self.__navigation_finished()

    def wait(self):
        """Call this to pause your program execution until the navigation
        request is complete."""
        self._nav_goal_finish_event.wait()

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

    def reset_position(self):
        self.robot_state.reset_pose()

    def stop(self):
        # don't call callback if user has terminated navigation manually
        self._on_finish = None

        self._stop_triggered = True
        try:
            self._sub_goal_nav_thread.join()
        except AttributeError:
            pass
        try:
            self._nav_thread.join()
        except AttributeError:
            pass
        self.__navigation_finished()
        self._drive_controller.stop()

    def __set_course_heading(self, x_goal, y_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__normalize_angle(theta - math.atan2(y_diff, x_diff))
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if self._goal_criteria.angle(heading_error):
                self.__sub_goal_reached()
                break

            self._drive_controller.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __drive_to_position_goal(self, x_goal, y_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x
            y_diff = y_goal - y

            heading_error = self.__get_angle_error(current_angle=theta, target_angle=math.atan2(y_diff, x_diff))
            distance_error = -np.hypot(x_diff, y_diff)
            if self._goal_criteria.distance(distance_error=distance_error, heading_error=heading_error):
                self.__sub_goal_reached()
                break

            angular_speed = self.__get_angular_speed(heading_error=heading_error)
            linear_speed = self.__get_linear_speed(distance_error=distance_error)

            self._drive_controller.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    def __rotate_to_angle_goal(self, theta_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose_update()

            heading_error = self.__get_angle_error(current_angle=theta, target_angle=theta_goal)
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if self._goal_criteria.angle(heading_error):
                self.__sub_goal_reached()
                break

            self._drive_controller.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __sub_goal_flow_control(self):
        self._sub_goal_nav_thread.start()
        self._nav_sub_goal_finish_event.wait()
        self._sub_goal_nav_thread.join()

    def __navigation_started(self):
        self._navigation_in_progress = True
        self._stop_triggered = False

    def __navigation_finished(self):
        self._nav_goal_finish_event.set()
        self._nav_goal_finish_event.clear()
        self._navigation_in_progress = False
        if callable(self._on_finish):
            self._on_finish()

    def __sub_goal_reached(self):
        self._drive_controller.stop()
        self._pid.reset()
        self._nav_sub_goal_finish_event.set()
        self._nav_sub_goal_finish_event.clear()

    def __get_new_pose_update(self):
        self._position_update_event.wait()
        self._position_update_event.clear()
        return self.robot_state.pose

    def __get_angle_error(self, current_angle, target_angle):
        return self.__normalize_angle(current_angle - target_angle)

    @staticmethod
    def __normalize_angle(angle):
        """Converts to range -pi to +pi to prevent unstable behaviour when
        going from 0 to 2*pi with slight turn.

        :param angle: angle in radians
        :return: angle in radians normalized to range -pi to +pi
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
        left_wheel_speed = self._drive_controller.left_motor.current_speed
        right_wheel_speed = self._drive_controller.right_motor.current_speed

        self.robot_state.v = (right_wheel_speed + left_wheel_speed) / 2.0
        self.robot_state.w = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation

        self.robot_state.x = self.robot_state.x + self.robot_state.v * np.cos(self.robot_state.theta) * dt
        self.robot_state.y = self.robot_state.y + self.robot_state.v * np.sin(self.robot_state.theta) * dt
        self.robot_state.theta = self.__normalize_angle(self.robot_state.theta + self.robot_state.w * dt)
