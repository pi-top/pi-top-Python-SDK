import math
import sched
import time
from inspect import getfullargspec
from threading import Event, Thread
from typing import Union

import numpy as np

from ..drive_controller import DriveController
from .core.driving_manager import DrivingManager
from .core.goal_criteria import GoalCriteria
from .core.robot_state import StateFilter
from .core.utils import normalize_angle


class NavigationController(DriveController):
    __VALID_ANGLE_RANGE = 180

    def __init__(
        self,
        left_motor_port: str = "M3",
        right_motor_port: str = "M0",
        linear_speed_factor: float = 0.75,
        angular_speed_factor: float = 0.5,
        name="navigate",
    ):
        """
        :param drive_controller: DriveController() object used to control motors
        :param linear_speed_factor: value between 0 and 1 for the linear speed
        :param angular_speed_factor: value between 0 and 1 for the angular speed
        """
        super().__init__(
            left_motor_port=left_motor_port,
            right_motor_port=right_motor_port,
            name=name,
        )

        # callback to call once navigation complete
        self._on_finish = None

        # Navigation algorithm flow control
        self.in_progress = False
        self._stop_triggered = False
        self._nav_goal_finish_event = Event()
        self._nav_thread = None
        self._sub_goal_nav_thread = None

        # Odometry updates
        self._measurement_frequency = 10.0  # Hz
        self._measurement_dt = 1.0 / self._measurement_frequency
        self._new_pose_event = Event()
        self._pose_prediction_scheduler = Thread(
            target=self.__measurement_scheduler, daemon=True
        )
        self._pose_prediction_scheduler.start()

        # Robot state tracking and driving management
        self.state_tracker = StateFilter(
            measurement_frequency=self._measurement_frequency,
            wheel_separation=self.wheel_separation,
        )
        self._drive_manager = DrivingManager(
            max_motor_speed=self.max_motor_speed,
            max_angular_speed=self.max_robot_angular_speed,
        )
        self._goal_criteria = GoalCriteria()
        self._backwards = False
        self.linear_speed_factor = linear_speed_factor
        self.angular_speed_factor = angular_speed_factor

    @property
    def own_state(self):
        return {"in_progress": self.in_progress}

    def go_to(
        self,
        position: Union[tuple, None] = None,
        angle: Union[float, int, None] = None,
        on_finish=None,
        backwards: bool = False,
    ):
        """Navigates the robot to a position (x, y) and/or angle where the
        starting position is assumed to be (0, 0) and the starting angle is
        assumed to be 0 degrees. Call function with .wait() appended to block
        program execution until the navigation goal has been achieved.

        Calling this function whilst another navigation goal is in progress will raise an error. Use the .wait()
        function to wait until navigation is completed or call .stop() if you wish to set a new navigation goal.

        :param Union[tuple, None] position: Position goal tuple in the form (x, y) where x and y are in meters (int or
                                            float).
        :param Union[float, int, None] angle: Desired angle of the robot in degrees.
        :param on_finish: A callable function or class to be called when the navigation goal has been reached.
        :param bool backwards: Go to navigation goal in reverse by setting to True
        :return NavigationController: self
        """
        self._on_finish = self.__check_callback(on_finish)

        if self.in_progress:
            raise RuntimeError(
                "Cannot call function before previous navigation is complete, use .wait() or call "
                ".stop() to cancel the previous navigation request."
            )

        if position is not None:
            if len(position) != 2 or type(position) not in (tuple, list):
                raise ValueError(
                    f"Position should be a list of size two in the form [x, y]. Received {position}."
                )
            if not all(isinstance(coordinate, (int, float)) for coordinate in position):
                raise ValueError("x and y coordinates must be of type int or float.")

        if angle is not None:
            if not (-self.__VALID_ANGLE_RANGE <= angle <= self.__VALID_ANGLE_RANGE):
                raise ValueError(
                    f"Angle must from {-self.__VALID_ANGLE_RANGE} to {self.__VALID_ANGLE_RANGE}."
                )

        self._backwards = backwards
        self._nav_thread = Thread(
            target=self.__navigate,
            args=(
                position,
                angle,
            ),
            daemon=True,
        )
        self._nav_thread.start()

        return self

    def __navigate(self, position, angle):
        self.__navigation_started()

        if position is not None:
            x, y = position
            self._sub_goal_nav_thread = Thread(
                target=self.__set_course_heading,
                args=(
                    x,
                    y,
                ),
                daemon=True,
            )
            self.__sub_goal_flow_control()
            self._sub_goal_nav_thread = Thread(
                target=self.__drive_to_position_goal,
                args=(
                    x,
                    y,
                ),
                daemon=True,
            )
            self.__sub_goal_flow_control()

        if angle is not None:
            self._sub_goal_nav_thread = Thread(
                target=self.__rotate_to_angle_goal,
                args=(math.radians(angle),),
                daemon=True,
            )
            self.__sub_goal_flow_control()

        self.__navigation_finished()

    def wait(self, timeout: Union[float, None] = None):
        """Call this to pause your program execution until the navigation
        request is complete."""
        self._nav_goal_finish_event.wait(timeout)

    @property
    def linear_speed_factor(self):
        """
        :return: current linear speed factor
        """
        return self._drive_manager.linear_speed_factor

    @linear_speed_factor.setter
    def linear_speed_factor(self, speed_factor: float):
        """Update the linear speed factor to change the speed that the robot
        will try to reach the goal position. Increasing this value will
        increase the uncertainty in the final navigation position. Setting to
        zero is not permitted.

        :param float speed_factor: Value greater than 0.0 and less than or equal to 1.0 where 1.0 is the maximum linear
        speed of the robot (which is based on maximum motor RPM and wheel circumference).
        """
        if not 0.0 < speed_factor <= 1.0:
            raise ValueError("Value must be in the range 0.0 < speed_factor <= 1.0")
        self._drive_manager.update_linear_speed(speed_factor)
        self._goal_criteria.update_linear_speed(speed_factor)

    @property
    def angular_speed_factor(self):
        """
        :return: current angular speed factor
        """
        return self._drive_manager.angular_speed_factor

    @angular_speed_factor.setter
    def angular_speed_factor(self, speed_factor):
        """Update the angular speed factor to change the speed that the robot
        will try to reach any angle goals. Increasing this value will increase
        the uncertainty in the final navigation position and angle. Setting to
        zero is not permitted.

        :param float speed_factor: Value greater than 0.0 and less than or equal to 1.0 where 1.0 is the maximum angular
        speed of the robot (which is based on maximum motor RPM, wheel circumference and wheel-to-wheel spacing).
        """
        if not 0.0 < speed_factor <= 1.0:
            raise ValueError("Value must be in the range 0.0 < speed_factor <= 1.0")
        self._drive_manager.update_angular_speed(speed_factor)
        self._goal_criteria.update_angular_speed(speed_factor)

    def reset_position_and_angle(self):
        """Reset the robot's position and angle (pose) to zeros."""
        self.state_tracker.reset_pose()

    def stop(self):
        """Terminate the navigation goal that is currently in progress and stop
        the robot's movement.

        Any on_finish callback function passed to the go_to() method
        will not be called if this function is called before the
        navigation goal has been reached.
        """
        self.stop_navigation()
        self.stop_movement()

    def stop_navigation(self):
        # don't call callback if user has terminated navigation manually
        self._on_finish = None

        self._stop_triggered = True
        try:
            self._sub_goal_nav_thread.join()
        except Exception:
            pass
        try:
            self._nav_thread.join()
        except Exception:
            pass
        self.__navigation_finished()

    def stop_movement(self):
        super().stop()

    def __set_course_heading(self, x_goal, y_goal):
        linear_speed = 0
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose()

            x_diff, y_diff = self.__get_position_error(
                x=x, x_goal=x_goal, y=y, y_goal=y_goal
            )
            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=math.atan2(y_diff, x_diff)
            )

            if self._goal_criteria.angle(angle_error):
                self.__sub_goal_reached()
                break

            angular_speed = self.__get_angular_speed(angle_error=angle_error)

            self.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    def __drive_to_position_goal(self, x_goal, y_goal):
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose()

            x_diff, y_diff = self.__get_position_error(
                x=x, x_goal=x_goal, y=y, y_goal=y_goal
            )
            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=math.atan2(y_diff, x_diff)
            )
            distance_error = (
                -np.hypot(x_diff, y_diff)
                if not self._backwards
                else np.hypot(x_diff, y_diff)
            )

            if self._goal_criteria.distance(
                distance_error=distance_error, angle_error=angle_error
            ):
                self.__sub_goal_reached()
                break

            angular_speed = self.__get_angular_speed(angle_error=angle_error)
            linear_speed = self.__get_linear_speed(distance_error=distance_error)

            self.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    def __rotate_to_angle_goal(self, theta_goal):
        linear_speed = 0
        while not self._stop_triggered:
            x, y, theta = self.__get_new_pose()

            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=theta_goal
            )

            if self._goal_criteria.angle(angle_error):
                self.__sub_goal_reached()
                break

            angular_speed = self.__get_angular_speed(angle_error=angle_error)

            self.robot_move(linear_speed=linear_speed, angular_speed=angular_speed)

    @staticmethod
    def __check_callback(on_finish):
        if on_finish is None:
            return None
        if callable(on_finish):
            arg_spec = getfullargspec(on_finish)
            number_of_arguments = len(arg_spec.args)
            number_of_default_arguments = (
                len(arg_spec.defaults) if arg_spec.defaults is not None else 0
            )
            if number_of_arguments == 0:
                return on_finish
            if (
                arg_spec.args[0] in ("self", "_mock_self")
                and (number_of_arguments - number_of_default_arguments) == 1
            ):
                return on_finish
            if number_of_arguments != number_of_default_arguments:
                raise ValueError(
                    "on_finish should have no non-default keyword arguments."
                )
        else:
            raise ValueError("on_finish should be a callable function.")

        return on_finish

    def __sub_goal_flow_control(self):
        self._sub_goal_nav_thread.start()
        self._sub_goal_nav_thread.join()

    def __navigation_started(self):
        self.in_progress = True
        self._stop_triggered = False

    def __navigation_finished(self):
        self.in_progress = False
        self._nav_goal_finish_event.set()
        self._nav_goal_finish_event.clear()
        if callable(self._on_finish):
            self._on_finish()

    def __sub_goal_reached(self):
        self.stop_movement()
        self._drive_manager.pid.reset()

    def __get_new_pose(self):
        self._new_pose_event.wait()
        return self.state_tracker.x, self.state_tracker.y, self.state_tracker.angle_rad

    @staticmethod
    def __get_angle_error(current_angle, target_angle):
        return normalize_angle(current_angle - target_angle)

    def __get_angular_speed(self, angle_error):
        return (
            self._drive_manager.max_angular_velocity
            * self._drive_manager.pid.heading(angle_error)
        )

    def __get_linear_speed(self, distance_error):
        return self._drive_manager.max_velocity * self._drive_manager.pid.distance(
            distance_error
        )

    def __get_position_error(self, x, x_goal, y, y_goal):
        x_diff = x_goal - x if not self._backwards else x - x_goal
        y_diff = y_goal - y if not self._backwards else y - y_goal
        return x_diff, y_diff

    def __measurement_scheduler(self):
        s = sched.scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(
            current_time + self._measurement_dt,
            1,
            self.__measurement_loop,
            (s, current_time),
        )
        s.run()

    def __measurement_loop(self, s, previous_time):
        current_time = time.time()
        dt = current_time - previous_time

        odom_measurements = self.__get_odometry_measurements()
        self.state_tracker.add_measurements(odom_measurements=odom_measurements, dt=dt)

        self._new_pose_event.set()
        self._new_pose_event.clear()

        s.enterabs(
            current_time + self._measurement_dt,
            1,
            self.__measurement_loop,
            (s, current_time),
        )

    def __get_odometry_measurements(self):
        left_wheel_speed = self.left_motor.current_speed
        right_wheel_speed = self.right_motor.current_speed
        linear_velocity = (right_wheel_speed + left_wheel_speed) / 2.0
        angular_velocity = (
            right_wheel_speed - left_wheel_speed
        ) / self.wheel_separation

        return np.array([[linear_velocity], [angular_velocity]])
