import logging
import math

import numpy as np

from .core.driving_manager import DrivingManager
from .core.goal_criteria import GoalCriteria
from .core.utils import normalize_angle

logger = logging.getLogger(__name__)


class Navigator:
    def __init__(
        self, max_motor_speed, max_robot_angular_speed, measurement_input_function
    ) -> None:
        if not callable(measurement_input_function):
            raise AttributeError(
                "Argument 'measurement_input_function' must be a function"
            )

        self.measurement_input_function = measurement_input_function
        self.backwards = False
        self._stop_triggered = False

        self.goal_criteria = GoalCriteria()
        self.drive_manager = DrivingManager(
            max_motor_speed=max_motor_speed,
            max_angular_speed=max_robot_angular_speed,
        )

    def navigate(self, position, angle):
        position_generators = []
        if position is not None:
            position_generators.append(self._set_course_heading(position))
            position_generators.append(self._drive_to_position_goal(position))
        if angle is not None:
            position_generators.append(self._rotate_to_angle_goal(math.radians(angle)))

        for generator in position_generators:
            for linear_speed, angular_speed in generator:
                yield linear_speed, angular_speed
            yield 0, 0
            self.drive_manager.pid.reset()

    def reached_position(self, position, angle=None):
        x_goal, y_goal = position
        x, y, theta = self.measurement_input_function()
        x_diff, y_diff = self.__get_position_error(
            x=x, x_goal=x_goal, y=y, y_goal=y_goal
        )
        angle_error = 0
        if angle:
            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=math.atan2(y_diff, x_diff)
            )
        return self.goal_criteria.distance(
            distance_error=self.__get_distance_error(x_diff=x_diff, y_diff=y_diff),
            angle_error=angle_error,
        )

    def _set_course_heading(self, position):
        x_goal, y_goal = position
        logger.debug(f"Navigator._set_course_heading - going to position {position}")
        while not self._stop_triggered:
            x, y, theta = self.measurement_input_function()
            logger.debug(
                f"Navigator._set_course_heading - (x, y, angle): ({x}, {y}, {math.degrees(theta)})"
            )
            x_diff, y_diff = self.__get_position_error(
                x=x, x_goal=x_goal, y=y, y_goal=y_goal
            )
            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=math.atan2(y_diff, x_diff)
            )
            logger.debug(
                "Navigator._set_course_heading - angle / goal / error : "
                f"{math.degrees(theta)} / {math.degrees(math.atan2(y_diff, x_diff))} / {math.degrees(angle_error)}"
            )

            if self.reached_position(position) or self.goal_criteria.angle(angle_error):
                logger.debug("Navigator._set_course_heading - arrived, exiting...")
                break

            linear_speed = 0
            angular_speed = self.drive_manager.get_new_angular_speed(
                angle_error=angle_error
            )
            yield linear_speed, angular_speed

    def _drive_to_position_goal(self, position):
        x_goal, y_goal = position
        logger.debug(
            f"Navigator._drive_to_position_goal - going to position {position}"
        )
        while not self._stop_triggered:
            x, y, theta = self.measurement_input_function()
            logger.debug(
                f"Navigator._drive_to_position_goal - (x, y, angle): ({x}, {y}, {math.degrees(theta)})"
            )

            x_diff, y_diff = self.__get_position_error(
                x=x, x_goal=x_goal, y=y, y_goal=y_goal
            )
            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=math.atan2(y_diff, x_diff)
            )
            distance_error = self.__get_distance_error(x_diff, y_diff)

            logger.debug(
                f"Navigator._drive_to_position_goal - distance error / angle_error : {distance_error} / {math.degrees(angle_error)}"
            )
            if self.goal_criteria.distance(
                distance_error=distance_error, angle_error=angle_error
            ):
                logger.debug("Navigator._drive_to_position_goal - arrived, exiting...")
                break

            angular_speed = self.drive_manager.get_new_angular_speed(
                angle_error=angle_error
            )
            linear_speed = self.drive_manager.get_new_linear_speed(
                distance_error=distance_error
            )
            yield linear_speed, angular_speed

    def _rotate_to_angle_goal(self, theta_goal):
        logger.debug(
            f"Navigator._rotate_to_angle_goal - going to angle {math.degrees(theta_goal)}"
        )
        while not self._stop_triggered:
            x, y, theta = self.measurement_input_function()
            logger.debug(
                f"Navigator._drive_to_position_goal - (x, y, angle): ({x}, {y}, {math.degrees(theta)})"
            )

            angle_error = self.__get_angle_error(
                current_angle=theta, target_angle=theta_goal
            )
            logger.debug(
                "Navigator._rotate_to_angle_goal - angle / goal / error : "
                f"{math.degrees(theta)} / {math.degrees(theta_goal)} / {math.degrees(angle_error)}"
            )

            if self.goal_criteria.angle(angle_error):
                logger.debug("Navigator._rotate_to_angle_goal - arrived, exiting...")
                break

            linear_speed = 0
            angular_speed = self.drive_manager.get_new_angular_speed(
                angle_error=angle_error
            )
            yield linear_speed, angular_speed

    def __get_angle_error(self, current_angle, target_angle):
        return normalize_angle(current_angle - target_angle)

    def __get_position_error(self, x, x_goal, y, y_goal):
        x_diff = x_goal - x if not self.backwards else x - x_goal
        y_diff = y_goal - y if not self.backwards else y - y_goal
        return x_diff, y_diff

    def __get_distance_error(self, x_diff, y_diff):
        value = np.hypot(x_diff, y_diff)
        if not self.backwards:
            return -value
        return value

    @property
    def angular_speed_factor(self):
        return self.drive_manager.angular_speed_factor

    @angular_speed_factor.setter
    def angular_speed_factor(self, speed_factor):
        if not 0.0 < speed_factor <= 1.0:
            raise ValueError("Value must be in the range 0.0 < speed_factor <= 1.0")
        self.drive_manager.update_angular_speed(speed_factor)
        self.goal_criteria.update_angular_speed(speed_factor)

    @property
    def linear_speed_factor(self):
        return self.drive_manager.linear_speed_factor

    @linear_speed_factor.setter
    def linear_speed_factor(self, speed_factor: float):
        if not 0.0 < speed_factor <= 1.0:
            raise ValueError("Value must be in the range 0.0 < speed_factor <= 1.0")
        self.drive_manager.update_linear_speed(speed_factor)
        self.goal_criteria.update_linear_speed(speed_factor)