from sys import modules
from unittest.mock import Mock, patch
from unittest import TestCase

modules_to_patch = [
    "pitop.camera.camera",
    "atexit",
    "numpy",
    "simple_pid",
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

from pitop import DriveController, EncoderMotor

# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


class DriveControllerTestCase(TestCase):

    def test_object_has_motorencoder_instances(self):
        """DriveController has a left and right EncoderMotor objects."""
        d = DriveController()
        self.assertTrue(isinstance(d.left_motor, EncoderMotor))
        self.assertTrue(isinstance(d.right_motor, EncoderMotor))

    def test_movement_method_call_robot_move(self):
        """'forward' method calls 'robot_move'."""
        d = DriveController()
        speed_factor = 1
        expected_linear_speed = speed_factor * d._max_motor_speed

        with patch.object(d, "robot_move") as robot_move_mock:
            d.forward(speed_factor, hold=False)
            robot_move_mock.assert_called_once_with(expected_linear_speed, 0)

    def test_forward_hold_param_stores_speed_for_next_movements(self):
        """'forward' hold parameter stores linear speed in object."""
        d = DriveController()
        speed_factor = 1
        expected_linear_speed = speed_factor * d._max_motor_speed

        d.forward(speed_factor, hold=True)
        self.assertEquals(d._linear_speed_x_hold, expected_linear_speed)

    def test_turning_methods_uses_internal_linear_speed(self):
        """turning left/right uses the internal linear speed to move."""
        d = DriveController()
        speed_factor = 1
        turn_radius = 0.1
        expected_linear_speed = speed_factor * d._max_motor_speed
        expected_angular_speed = d._max_robot_angular_speed * speed_factor
        d._linear_speed_x_hold = expected_linear_speed

        with patch.object(d, "robot_move") as robot_move_mock:
            d.left(speed_factor, turn_radius=turn_radius)
            robot_move_mock.assert_called_once_with(expected_linear_speed,
                                                    expected_angular_speed,
                                                    turn_radius)

    def test_turn_right_calls_left_method(self):
        """'right' calls 'left' method with inverted parameters."""
        d = DriveController()
        speed_factor = 1
        turn_radius = 0.1

        with patch.object(d, "left") as left_mock:
            d.right(speed_factor, turn_radius=turn_radius)
            left_mock.assert_called_once_with(-speed_factor, -turn_radius)

    def test_backward_calls_forward_method(self):
        """'backward' calls 'forward' method with inverted parameters."""
        d = DriveController()
        speed_factor = 1
        hold = False

        with patch.object(d, "forward") as forward_mock:
            d.backward(speed_factor, hold=hold)
            forward_mock.assert_called_once_with(-speed_factor, hold)

    def test_stop_sets_angular_and_linear_speeds_to_zero(self):
        """'stop' method sets angular & linear speeds to zero."""
        d = DriveController()

        with patch.object(d, "robot_move") as robot_move_mock:
            d.stop()
            robot_move_mock.assert_called_once_with(0, 0)

    def test_stop_rotation_sets_angular_speed_to_zero(self):
        """'stop_rotation' method sets angular speed to zero."""
        d = DriveController()
        linear_speed = 0.5
        d._linear_speed_x_hold = linear_speed

        with patch.object(d, "robot_move") as robot_move_mock:
            d.stop_rotation()
            robot_move_mock.assert_called_once_with(linear_speed, 0)

    def test_rotate_fails_on_invalid_time(self):
        """'rotate' method fails if 'time_to_take' parameter is invalid."""
        d = DriveController()
        for time_to_take in (-1, 0):
            with self.assertRaises(AssertionError):
                d.rotate(0, time_to_take)

    def test_motor_rpm_calculations_based_on_speeds(self):
        """motor speed calculations based on linear/angular speeds."""
        d = DriveController()

        test_values = [
            [0, 0, 0, 0, 0],
            [0.378, 0.447, 1, 1, 0],
            [0.411, 0.447, 1, 1, 1],
            [0.275, 0.325, 0.3, 0.3, 0],
            [0.407, 0.447, 0.3, 0.3, 0.8],
        ]
        for exp_rpm_left, exp_rpm_right, linear_speed, angular_speed, turn_radius in test_values:
            speed_left, speed_right = d._calculate_motor_speeds(linear_speed, angular_speed, turn_radius)
            self.assertEquals(round(speed_left, 3), exp_rpm_left)
            self.assertEquals(round(speed_right, 3), exp_rpm_right)
