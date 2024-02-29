from threading import Event, Thread
from typing import Union

import numpy as np

from ..drive_controller import DriveController
from .core.measurement_scheduler import MeasurementScheduler
from .core.robot_state import StateFilter
from .core.utils import verify_callback
from .navigator import Navigator


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
        :param left_motor_port: string with the name of the port for the left motor
        :param right_motor_port: string with the name of the port for the right motor
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
        self._nav_goal_finish_event = Event()
        self._nav_thread = None

        self._measurement_frequency = 10.0  # Hz

        # Robot state tracking and driving management
        self.state_tracker = StateFilter(
            measurement_frequency=self._measurement_frequency,
            wheel_separation=self.wheel_separation,
        )

        self.navigator = Navigator(
            max_motor_speed=self.max_motor_speed,
            max_robot_angular_speed=self.max_robot_angular_speed,
            measurement_input_function=lambda: self.pose,
        )

        # Odometry updates
        self.measurement_scheduler = MeasurementScheduler(
            measurement_frequency=self._measurement_frequency,
            measurement_input_function=lambda: self.odometry,
            state_tracker=self.state_tracker,
        )

        self.linear_speed_factor = linear_speed_factor
        self.angular_speed_factor = angular_speed_factor

    @property
    def own_state(self):
        return {
            "in_progress": self.in_progress,
            "tracker": self.state_tracker.own_state,
        }

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

        Calling this function whilst another navigation goal is in
        progress will raise an error. Use the .wait() function to wait
        until navigation is completed or call .stop() if you wish to set
        a new navigation goal.

        :param Union[tuple, None] position: Position goal tuple in the
        form (x, y) where x and y are in meters (int or float). :param
        Union[float, int, None] angle: Desired angle of the robot in
        degrees.
        :param on_finish: A callable function or class to be called when
            the navigation goal has been reached.
        :param bool backwards: Go to navigation goal in reverse by
            setting to True
        :return NavigationController: self
        """
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

        self._on_finish = verify_callback(on_finish)
        self._nav_thread = Thread(
            target=self.__navigate,
            args=(
                position,
                angle,
                backwards,
            ),
            daemon=True,
        )
        self._nav_thread.start()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()

    def __navigate(self, position, angle, backwards):
        self.__navigation_started()

        self.navigator.backwards = backwards
        for linear_speed, angular_speed in self.navigator.navigate(position, angle):
            self.robot_move(
                linear_speed=linear_speed,
                angular_speed=angular_speed,
            )

        self.__navigation_finished()

    def wait(self, timeout: Union[float, None] = None):
        """Call this to pause your program execution until the navigation
        request is complete."""
        self._nav_goal_finish_event.wait(timeout)

    @property
    def pose(self):
        self.measurement_scheduler.wait_for_measurement()
        return self.state_tracker.x, self.state_tracker.y, self.state_tracker.angle_rad

    @property
    def odometry(self):
        left_wheel_speed = self.left_motor.current_speed
        right_wheel_speed = self.right_motor.current_speed
        linear_velocity = (right_wheel_speed + left_wheel_speed) / 2.0
        angular_velocity = (
            right_wheel_speed - left_wheel_speed
        ) / self.wheel_separation

        return np.array([[linear_velocity], [angular_velocity]])

    @property
    def linear_speed_factor(self):
        """
        :return: current linear speed factor
        """
        return self.navigator.linear_speed_factor

    @linear_speed_factor.setter
    def linear_speed_factor(self, speed_factor: float):
        """Update the linear speed factor to change the speed that the robot
        will try to reach the goal position. Increasing this value will
        increase the uncertainty in the final navigation position. Setting to
        zero is not permitted.

        :param float speed_factor: Value greater than 0.0 and less than
            or equal to 1.0 where 1.0 is the maximum linear speed of the
            robot (which is based on maximum motor RPM and wheel
            circumference).
        """
        self.navigator.linear_speed_factor = speed_factor

    @property
    def angular_speed_factor(self):
        """
        :return: current angular speed factor
        """
        return self.navigator.angular_speed_factor

    @angular_speed_factor.setter
    def angular_speed_factor(self, speed_factor):
        """Update the angular speed factor to change the speed that the robot
        will try to reach any angle goals. Increasing this value will increase
        the uncertainty in the final navigation position and angle. Setting to
        zero is not permitted.

        :param float speed_factor: Value greater than 0.0 and less than
            or equal to 1.0 where 1.0 is the maximum angular speed of
            the robot (which is based on maximum motor RPM, wheel
            circumference and wheel-to-wheel spacing).
        """
        self.navigator.angular_speed_factor = speed_factor

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
        self.navigator._stop_triggered = True
        try:
            self._nav_thread.join()
        except Exception:
            raise
        self.__navigation_finished()

    def stop_movement(self):
        super().stop()

    def __navigation_started(self):
        self.in_progress = True
        self.navigator._stop_triggered = False

    def __navigation_finished(self):
        self.in_progress = False
        self._nav_goal_finish_event.set()
        self._nav_goal_finish_event.clear()
        if callable(self._on_finish):
            self._on_finish()
