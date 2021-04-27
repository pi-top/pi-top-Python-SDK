from threading import Thread, Event
import time
import numpy as np
import math
from typing import Union
from simple_pid import PID
import sched
from inspect import getfullargspec
from .utils import normalize_angle
from .robot_state import RobotState


class GoalCriteria:
    def __init__(self, full_speed_distance_error=0.02, full_speed_angle_error=4.0):
        self._full_speed_distance_error = full_speed_distance_error
        self._full_speed_angle_error = math.radians(full_speed_angle_error)

        self._max_distance_error = None
        self._max_angle_error = None

    def angle(self, angle_error):
        return abs(angle_error) < self._max_angle_error

    def distance(self, distance_error, heading_error):
        if abs(distance_error) < self._max_distance_error:
            return True
        if abs(heading_error) > math.pi / 2:
            # Overshot goal, error will be small so consider goal to be reached.
            # Otherwise robot would have to reverse a tiny amount which would be poor UX.
            # Robot will correct itself on subsequent navigation calls anyway.
            return True
        return False

    def update_linear_speed(self, speed_factor):
        self._max_distance_error = speed_factor * self._full_speed_distance_error

    def update_angular_speed(self, speed_factor):
        self._max_angle_error = speed_factor * self._full_speed_angle_error


class RobotDrivingManager:
    class PIDManager:
        def __init__(self):
            self._Ki = 0.1
            self._Kd = 0.1
            self.distance = PID(Kp=0.0,
                                Ki=self._Ki,
                                Kd=self._Kd,
                                setpoint=0.0,
                                output_limits=(-1.0, 1.0)
                                )
            self.heading = PID(Kp=0.0,
                               Ki=self._Ki,
                               Kd=self._Kd,
                               setpoint=0.0,
                               output_limits=(-1.0, 1.0)
                               )

        def reset(self):
            self.heading.reset()
            self.distance.reset()

        def distance_update(self, deceleration_distance):
            self.distance.Kp = 1.0 / deceleration_distance

        def heading_update(self, deceleration_angle):
            self.heading.Kp = 1.0 / deceleration_angle

    def __init__(self,
                 max_motor_speed,
                 max_angular_speed,
                 full_speed_deceleration_distance=0.4,
                 full_speed_deceleration_angle=120.0
                 ):
        self._max_motor_speed = max_motor_speed                             # m/s
        self._max_angular_speed = max_angular_speed                         # rad/s
        self._max_deceleration_distance = full_speed_deceleration_distance  # m
        self._max_deceleration_angle = full_speed_deceleration_angle        # degrees

        self.linear_speed_factor = None
        self.angular_speed_factor = None
        self.max_velocity = None
        self.max_angular_velocity = None
        self.deceleration_distance = None
        self.deceleration_angle = None
        self.pid = self.PIDManager()

    def update_linear_speed(self, speed_factor):
        self.linear_speed_factor = speed_factor
        self.max_velocity = self.linear_speed_factor * self._max_motor_speed
        self.deceleration_distance = self.linear_speed_factor * self._max_deceleration_distance
        self.pid.distance_update(deceleration_distance=self.deceleration_distance)

    def update_angular_speed(self, speed_factor):
        self.angular_speed_factor = speed_factor
        self.max_angular_velocity = self.angular_speed_factor * self._max_angular_speed
        self.deceleration_angle = self.angular_speed_factor * math.radians(self._max_deceleration_angle)
        self.pid.heading_update(deceleration_angle=self.deceleration_angle)


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
        self._nav_thread = None
        self._sub_goal_nav_thread = None

        # Odometry tracking
        self._odom_update_frequency = 10.0  # Hz
        self._odom_update_schedule = 1.0 / self._odom_update_frequency
        self._position_update_event = Event()
        self._odometry_tracker = Thread(target=self.__track_odometry, daemon=True)
        self._odometry_tracker.start()

        # Robot state and control
        self._backwards = False
        self.robot_state = RobotState()
        self._drive_controller = drive_controller
        self._drive_manager = RobotDrivingManager(max_motor_speed=self._drive_controller.max_motor_speed,
                                                  max_angular_speed=self._drive_controller.max_robot_angular_speed
                                                  )
        self._goal_criteria = GoalCriteria()
        self.linear_speed_factor = linear_speed_factor
        self.angular_speed_factor = angular_speed_factor

    def go_to(self,
              position: Union[tuple, None] = None,
              angle: Union[float, None] = None,
              on_finish=None,
              backwards: bool = False
              ):

        self._on_finish = self.__check_callback(on_finish)

        if self._navigation_in_progress:
            raise RuntimeError("Cannot call function before previous navigation is complete, use .wait() or call "
                               ".stop() to cancel the previous navigation request.")

        if position is not None:
            if len(position) != 2 or type(position) is not tuple:
                raise ValueError("Position should be a list of size two in the form [x, y].")
            if not all(isinstance(coordinate, (int, float)) for coordinate in position):
                raise ValueError("x and y coordinates must be of type int or float.")

        if angle is not None:
            if not (-self.__VALID_ANGLE_RANGE <= angle <= self.__VALID_ANGLE_RANGE):
                raise ValueError(f"Angle must from {-self.__VALID_ANGLE_RANGE} to {self.__VALID_ANGLE_RANGE}.")

        self._backwards = backwards
        self._nav_thread = Thread(target=self.__navigate, args=(position, angle, ), daemon=True)
        self._nav_thread.start()

        return self

    def __navigate(self, position, angle):
        self.__navigation_started()

        if position is not None:
            x, y = position
            self._sub_goal_nav_thread = Thread(target=self.__set_course_heading, args=(x, y, ), daemon=True)
            self.__sub_goal_flow_control()
            self._sub_goal_nav_thread = Thread(target=self.__drive_to_position_goal, args=(x, y, ), daemon=True)
            self.__sub_goal_flow_control()

        if angle is not None:
            self._sub_goal_nav_thread = Thread(target=self.__rotate_to_angle_goal,
                                               args=(math.radians(angle), ),
                                               daemon=True
                                               )
            self.__sub_goal_flow_control()

        self.__navigation_finished()

    def wait(self, timeout: Union[float, None] = None):
        """Call this to pause your program execution until the navigation
        request is complete."""
        self._nav_goal_finish_event.wait(timeout)

    @property
    def linear_speed_factor(self):
        return self._drive_manager.linear_speed_factor

    @linear_speed_factor.setter
    def linear_speed_factor(self, speed_factor):
        self._drive_manager.update_linear_speed(speed_factor)
        self._goal_criteria.update_linear_speed(speed_factor)

    @property
    def angular_speed_factor(self):
        return self._drive_manager.angular_speed_factor

    @angular_speed_factor.setter
    def angular_speed_factor(self, speed_factor):
        self._drive_manager.update_angular_speed(speed_factor)
        self._goal_criteria.update_angular_speed(speed_factor)

    def reset_position_and_angle(self):
        self.robot_state.reset_pose()

    def stop(self):
        # don't call callback if user has terminated navigation manually
        self._on_finish = None

        self._stop_triggered = True
        try:
            self._sub_goal_nav_thread.join()
        except RuntimeError:
            pass
        try:
            self._nav_thread.join()
        except RuntimeError:
            pass
        self.__navigation_finished()
        self._drive_controller.stop()

    def __set_course_heading(self, x_goal, y_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x if not self._backwards else x - x_goal
            y_diff = y_goal - y if not self._backwards else y - y_goal

            heading_error = normalize_angle(theta - math.atan2(y_diff, x_diff))
            angular_speed = self.__get_angular_speed(heading_error=heading_error)

            if self._goal_criteria.angle(heading_error):
                self.__sub_goal_reached()
                break

            self._drive_controller.robot_move(linear_speed=0, angular_speed=angular_speed)

    def __drive_to_position_goal(self, x_goal, y_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose_update()

            x_diff = x_goal - x if not self._backwards else x - x_goal
            y_diff = y_goal - y if not self._backwards else y - y_goal

            heading_error = self.__get_angle_error(current_angle=theta, target_angle=math.atan2(y_diff, x_diff))
            distance_error = -np.hypot(x_diff, y_diff) if not self._backwards else np.hypot(x_diff, y_diff)

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

    @staticmethod
    def __check_callback(on_finish):
        if on_finish is None:
            return None
        if callable(on_finish):
            arg_spec = getfullargspec(on_finish)
            number_of_arguments = len(arg_spec.args)
            number_of_default_arguments = len(arg_spec.defaults) if arg_spec.defaults is not None else 0
            if number_of_arguments != number_of_default_arguments:
                raise ValueError("on_finish should have no non-default keyword arguments.")
        else:
            raise ValueError("on_finish should be a callable function.")

        return on_finish

    def __sub_goal_flow_control(self):
        self._sub_goal_nav_thread.start()
        self._sub_goal_nav_thread.join()

    def __navigation_started(self):
        self._navigation_in_progress = True
        self._stop_triggered = False

    def __navigation_finished(self):
        self._position_update_event.wait()  # wait for another position update before returning to user program
        self._navigation_in_progress = False
        self._nav_goal_finish_event.set()
        self._nav_goal_finish_event.clear()
        if callable(self._on_finish):
            self._on_finish()

    def __sub_goal_reached(self):
        self._drive_controller.stop()
        self._drive_manager.pid.reset()

    def __get_new_pose_update(self):
        self._position_update_event.wait()
        return self.robot_state.x, self.robot_state.y, self.robot_state.angle_rad

    def __get_angle_error(self, current_angle, target_angle):
        return normalize_angle(current_angle - target_angle)

    def __get_angular_speed(self, heading_error):
        return self._drive_manager.max_angular_velocity * self._drive_manager.pid.heading(heading_error)

    def __get_linear_speed(self, distance_error):
        return self._drive_manager.max_velocity * self._drive_manager.pid.distance(distance_error)

    def __track_odometry(self):
        s = sched.scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(current_time + self._odom_update_schedule, 1, self.__update_state, (s, current_time))
        s.run()

    def __update_state(self, s, previous_time):
        current_time = time.time()
        dt = current_time - previous_time

        left_wheel_speed = self._drive_controller.left_motor.current_speed
        right_wheel_speed = self._drive_controller.right_motor.current_speed

        linear_velocity = (right_wheel_speed + left_wheel_speed) / 2.0
        angular_velocity = (right_wheel_speed - left_wheel_speed) / self._drive_controller.wheel_separation

        self.robot_state.kalman_predict(u=np.array([[linear_velocity],
                                                    [angular_velocity]]),
                                        dt=dt
                                        )

        self._position_update_event.set()
        self._position_update_event.clear()

        s.enterabs(current_time + self._odom_update_schedule, 1, self.__update_state, (s, current_time))
