import math
from time import sleep
from unittest.mock import MagicMock, patch

import pytest


class EncoderMotorSim:
    _SPEED_NOISE_SIGMA_RATIO = 0.05

    def __init__(self, *args, **kwargs):
        self.max_speed = 0.428
        self.wheel_diameter = 0.0718
        self._target_speed = 0.0
        self._motor_speed_update_schedule = 1.0 / 20.0

    @property
    def current_speed(self):
        return self._target_speed

    def set_target_speed(self, target_speed, direction=None, distance=None):
        self._target_speed = target_speed


@patch("pitop.robotics.drive_controller.EncoderMotor", EncoderMotorSim)
def get_navigation_controller():
    from pitop.robotics.navigation.navigation_controller import NavigationController

    return NavigationController()


def robot_state_assertions(
    navigation_controller, x_expected, y_expected, angle_expected
):
    sleep(0.25)  # give robot time to slow down
    assert math.isclose(navigation_controller.state_tracker.x, x_expected, abs_tol=1)
    assert math.isclose(navigation_controller.state_tracker.y, y_expected, abs_tol=1)
    assert abs(navigation_controller.state_tracker.angle - angle_expected) < 4
    assert math.isclose(navigation_controller.state_tracker.v, 0, abs_tol=1)
    assert math.isclose(navigation_controller.state_tracker.w, 0, abs_tol=1)


def test_navigate_to_x_y_position():
    navigation_controller = get_navigation_controller()
    x_goal = 0.25
    y_goal = -0.25
    resulting_angle = math.degrees(math.atan2(y_goal, x_goal))

    navigation_controller.go_to(position=(x_goal, y_goal), angle=None).wait()

    robot_state_assertions(
        navigation_controller=navigation_controller,
        x_expected=x_goal,
        y_expected=y_goal,
        angle_expected=resulting_angle,
    )


def test_navigate_to_angle():
    navigation_controller = get_navigation_controller()
    angle_goal = 87
    navigation_controller.go_to(position=None, angle=angle_goal).wait()

    robot_state_assertions(
        navigation_controller=navigation_controller,
        x_expected=0,
        y_expected=0,
        angle_expected=angle_goal,
    )


def test_navigate_to_position_and_angle():
    navigation_controller = get_navigation_controller()
    x_goal = 0.1
    y_goal = -0.2
    angle_goal = -97
    navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal).wait()

    robot_state_assertions(
        navigation_controller=navigation_controller,
        x_expected=x_goal,
        y_expected=y_goal,
        angle_expected=angle_goal,
    )


def test_navigate_to_position_and_angle_backwards():
    navigation_controller = get_navigation_controller()
    x_goal = 0.2
    y_goal = -0.2
    angle_goal = 32
    navigation_controller.go_to(
        position=(x_goal, y_goal), angle=angle_goal, backwards=True
    ).wait()

    robot_state_assertions(
        navigation_controller=navigation_controller,
        x_expected=x_goal,
        y_expected=y_goal,
        angle_expected=angle_goal,
    )


def test_invalid_callback():
    def invalid_callback(parameter):
        pass

    navigation_controller = get_navigation_controller()
    x_goal = 0.1
    y_goal = 0

    with pytest.raises(ValueError):
        navigation_controller.go_to(
            position=(x_goal, y_goal), on_finish=invalid_callback
        )


def test_kalman_filter_covariance_increases():
    navigation_controller = get_navigation_controller()
    x_goal = -0.2
    y_goal = -0.05
    angle_goal = -10

    x_tolerance_start = navigation_controller.state_tracker.x_tolerance
    y_tolerance_start = navigation_controller.state_tracker.y_tolerance
    angle_tolerance_start = navigation_controller.state_tracker.angle_tolerance

    navigation_controller.go_to(
        position=(x_goal, y_goal), angle=angle_goal, backwards=True
    ).wait()

    x_tolerance_end = navigation_controller.state_tracker.x_tolerance
    y_tolerance_end = navigation_controller.state_tracker.y_tolerance
    angle_tolerance_end = navigation_controller.state_tracker.angle_tolerance

    robot_state_assertions(
        navigation_controller=navigation_controller,
        x_expected=x_goal,
        y_expected=y_goal,
        angle_expected=angle_goal,
    )
    assert x_tolerance_end > x_tolerance_start
    assert y_tolerance_end > y_tolerance_start
    assert angle_tolerance_end > angle_tolerance_start


def test_callback_function_is_called():
    navigation_controller = get_navigation_controller()

    x_goal = 0.143
    y_goal = -0.189
    angle_goal = 8

    mock = MagicMock()
    navigation_controller.go_to(
        position=(x_goal, y_goal), angle=angle_goal, on_finish=mock.method
    ).wait()

    mock.method.assert_called_once()


def test_stop_function():
    navigation_controller = get_navigation_controller()

    x_goal = -0.143
    y_goal = 0.189
    angle_goal = -14.32

    mock = MagicMock()
    navigation_controller.go_to(
        position=(x_goal, y_goal), angle=angle_goal, on_finish=mock.method
    )
    navigation_controller.stop()
    mock.method.assert_not_called()
    sleep(0.25)
    assert math.isclose(navigation_controller.state_tracker.v, 0, abs_tol=1)
    assert math.isclose(navigation_controller.state_tracker.w, 0, abs_tol=1)


def test_update_speed_factors():
    navigation_controller = get_navigation_controller()

    linear_speed_factor = 0.1
    angular_speed_factor = 0.1
    navigation_controller.linear_speed_factor = linear_speed_factor
    navigation_controller.angular_speed_factor = angular_speed_factor

    assert navigation_controller.linear_speed_factor == linear_speed_factor
    assert navigation_controller.angular_speed_factor == angular_speed_factor

    assert (
        navigation_controller.navigator.goal_criteria._max_distance_error
        == navigation_controller.navigator.goal_criteria._full_speed_distance_error
        * linear_speed_factor
    )
    assert (
        navigation_controller.navigator.goal_criteria._max_angle_error
        == navigation_controller.navigator.goal_criteria._full_speed_angle_error
        * angular_speed_factor
    )

    assert navigation_controller.navigator.drive_manager.pid.distance.Kp == 1 / (
        navigation_controller.navigator.drive_manager._full_speed_deceleration_distance
        * linear_speed_factor
    )

    assert navigation_controller.navigator.drive_manager.pid.heading.Kp == 0.7
