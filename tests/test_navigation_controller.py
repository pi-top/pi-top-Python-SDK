from sys import modules
from unittest.mock import Mock, patch
from unittest import TestCase

modules_to_patch = [
    "atexit",
    "pitopcommon.common_ids",
    "pitopcommon.current_session_info",
    "pitopcommon.ptdm",
    "pitopcommon.firmware_device",
    "pitopcommon.command_runner",
    "pitopcommon.common_names",
    "pitopcommon.smbus_device",
    "pitopcommon.logger",
    "pitopcommon.singleton",
]
for module in modules_to_patch:
    modules[module] = Mock()

from pitop.robotics.drive_controller import DriveController
from pitop.robotics.navigation.navigation_controller import NavigationController
import math
from time import sleep


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


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


class TestNavigationController(TestCase):

    def test_navigate_to_x_y_position(self):
        navigation_controller = self.get_navigation_controller()
        x_goal = 0.25
        y_goal = -0.25
        resulting_angle = math.degrees(math.atan2(y_goal, x_goal))

        navigation_controller.go_to(position=(x_goal, y_goal), angle=None).wait()

        self.robot_state_assertions(navigation_controller=navigation_controller,
                                    x_expected=x_goal,
                                    y_expected=y_goal,
                                    angle_expected=resulting_angle
                                    )

    def test_navigate_to_angle(self):
        navigation_controller = self.get_navigation_controller()
        angle_goal = 87
        navigation_controller.go_to(position=None, angle=angle_goal).wait()

        self.robot_state_assertions(navigation_controller=navigation_controller,
                                    x_expected=0,
                                    y_expected=0,
                                    angle_expected=angle_goal
                                    )

    def test_navigate_to_position_and_angle(self):
        navigation_controller = self.get_navigation_controller()
        x_goal = 0.1
        y_goal = -0.2
        angle_goal = -97
        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal).wait()

        self.robot_state_assertions(navigation_controller=navigation_controller,
                                    x_expected=x_goal,
                                    y_expected=y_goal,
                                    angle_expected=angle_goal
                                    )

    def test_navigate_to_position_and_angle_backwards(self):
        navigation_controller = self.get_navigation_controller()
        x_goal = 0.2
        y_goal = -0.2
        angle_goal = 32
        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal, backwards=True).wait()

        self.robot_state_assertions(navigation_controller=navigation_controller,
                                    x_expected=x_goal,
                                    y_expected=y_goal,
                                    angle_expected=angle_goal
                                    )

    def test_invalid_callback(self):
        def invalid_callback(parameter):
            pass

        navigation_controller = self.get_navigation_controller()
        x_goal = 0.1
        y_goal = 0
        self.assertRaises(ValueError,
                          navigation_controller.go_to,
                          position=(x_goal, y_goal),
                          on_finish=invalid_callback
                          )

    def test_kalman_filter_covariance_increases(self):
        navigation_controller = self.get_navigation_controller()
        x_goal = -0.2
        y_goal = -0.05
        angle_goal = -10

        x_tolerance_start = navigation_controller.state.x_tolerance
        y_tolerance_start = navigation_controller.state.y_tolerance
        angle_tolerance_start = navigation_controller.state.angle_tolerance

        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal, backwards=True).wait()

        x_tolerance_end = navigation_controller.state.x_tolerance
        y_tolerance_end = navigation_controller.state.y_tolerance
        angle_tolerance_end = navigation_controller.state.angle_tolerance

        self.robot_state_assertions(navigation_controller=navigation_controller,
                                    x_expected=x_goal,
                                    y_expected=y_goal,
                                    angle_expected=angle_goal
                                    )
        self.assertGreater(x_tolerance_end, x_tolerance_start)
        self.assertGreater(y_tolerance_end, y_tolerance_start)
        self.assertGreater(angle_tolerance_end, angle_tolerance_start)

    def test_callback_function_is_called(self):
        navigation_controller = self.get_navigation_controller()

        x_goal = 0.143
        y_goal = -0.189
        angle_goal = 8

        mock = Mock()
        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal, on_finish=mock.method).wait()

        mock.method.assert_called_once()

    def test_stop_function(self):
        navigation_controller = self.get_navigation_controller()

        x_goal = -0.143
        y_goal = 0.189
        angle_goal = -14.32

        mock = Mock()
        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal, on_finish=mock.method)
        navigation_controller.stop()
        mock.method.assert_not_called()
        sleep(0.25)
        self.assertAlmostEqual(navigation_controller.state.v, 0, places=1)
        self.assertAlmostEqual(navigation_controller.state.w, 0, places=1)

    def test_update_speed_factors(self):
        navigation_controller = self.get_navigation_controller()

        linear_speed_factor = 0.1
        angular_speed_factor = 0.1
        navigation_controller.linear_speed_factor = linear_speed_factor
        navigation_controller.angular_speed_factor = angular_speed_factor

        self.assertEqual(navigation_controller.linear_speed_factor, linear_speed_factor)
        self.assertEqual(navigation_controller.angular_speed_factor, angular_speed_factor)

        self.assertEqual(navigation_controller._goal_criteria._max_distance_error,
                         navigation_controller._goal_criteria._full_speed_distance_error * linear_speed_factor
                         )
        self.assertEqual(navigation_controller._goal_criteria._max_angle_error,
                         navigation_controller._goal_criteria._full_speed_angle_error * angular_speed_factor
                         )

        self.assertEqual(navigation_controller._drive_manager.pid.distance.Kp,
                         1 / (navigation_controller._drive_manager._max_deceleration_distance * linear_speed_factor))

        self.assertEqual(navigation_controller._drive_manager.pid.heading.Kp,
                         1 / (math.radians(navigation_controller._drive_manager._max_deceleration_angle)
                              * angular_speed_factor)
                         )

    @staticmethod
    @patch("pitop.robotics.drive_controller.EncoderMotor", EncoderMotorSim)
    def get_navigation_controller():
        return NavigationController(drive_controller=DriveController())

    def robot_state_assertions(self, navigation_controller, x_expected, y_expected, angle_expected):
        sleep(0.25)  # give robot time to slow down
        self.assertAlmostEqual(navigation_controller.state.x, x_expected, places=1)
        self.assertAlmostEqual(navigation_controller.state.y, y_expected, places=1)
        self.assertAlmostEqual(navigation_controller.state.angle, angle_expected, delta=4)
        self.assertAlmostEqual(navigation_controller.state.v, 0, places=1)
        self.assertAlmostEqual(navigation_controller.state.w, 0, places=1)
