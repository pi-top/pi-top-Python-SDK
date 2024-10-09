from unittest import TestCase
from unittest.mock import patch

from pitop import DriveController, EncoderMotor


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
        expected_linear_speed = speed_factor * d.max_motor_speed

        with patch.object(d, "robot_move") as robot_move_mock:
            d.forward(speed_factor, hold=False, distance=None)
            robot_move_mock.assert_called_once_with(
                linear_speed=expected_linear_speed, angular_speed=0, distance=None
            )

    def test_forward_hold_param_stores_speed_for_next_movements(self):
        """'forward' hold parameter stores linear speed in object."""
        d = DriveController()
        speed_factor = 1
        expected_linear_speed = speed_factor * d.max_motor_speed

        d.forward(speed_factor, hold=True)
        self.assertEqual(d._linear_speed_x_hold, expected_linear_speed)

    def test_turning_methods_uses_internal_linear_speed(self):
        """Turning left/right uses the internal linear speed to move."""
        d = DriveController()
        speed_factor = 1
        turn_radius = 0.1
        expected_linear_speed = speed_factor * d.max_motor_speed
        expected_angular_speed = d.max_robot_angular_speed * speed_factor
        d._linear_speed_x_hold = expected_linear_speed

        with patch.object(d, "robot_move") as robot_move_mock:
            d.left(speed_factor, turn_radius=turn_radius)
            robot_move_mock.assert_called_once_with(
                linear_speed=expected_linear_speed,
                angular_speed=expected_angular_speed,
                turn_radius=turn_radius,
                distance=None,
            )

    def test_turn_right_calls_left_method(self):
        """'right' calls 'left' method with inverted parameters."""
        d = DriveController()
        speed_factor = 1
        turn_radius = 0.1

        with patch.object(d, "left") as left_mock:
            d.right(speed_factor, turn_radius=turn_radius)
            left_mock.assert_called_once_with(-speed_factor, -turn_radius, None)

    def test_backward_calls_forward_method(self):
        """'backward' calls 'forward' method with inverted parameters."""
        d = DriveController()
        speed_factor = 1
        hold = False
        distance = None

        with patch.object(d, "forward") as forward_mock:
            d.backward(speed_factor, hold=hold)
            forward_mock.assert_called_once_with(-speed_factor, hold, distance)

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
        """Motor speed calculations based on linear/angular speeds."""
        d = DriveController()

        test_values = [
            [0, 0, 0, 0, 0],
            [0.38, 0.447, 1, 1, 0],
            [0.412, 0.447, 1, 1, 1],
            [0.276, 0.324, 0.3, 0.3, 0],
            [0.408, 0.447, 0.3, 0.3, 0.8],
        ]
        for (
            exp_rpm_left,
            exp_rpm_right,
            linear_speed,
            angular_speed,
            turn_radius,
        ) in test_values:
            speed_left, speed_right = d._calculate_motor_speeds(
                linear_speed, angular_speed, turn_radius
            )
            self.assertEqual(round(speed_left, 3), exp_rpm_left)
            self.assertEqual(round(speed_right, 3), exp_rpm_right)

    def test_rotate_speeds(self):
        """Rotate method doesn't use max speed by default."""

        sleep_mock = patch("pitop.robotics.drive_controller.sleep").start()
        d = DriveController()
        with patch.object(d, "_set_motor_speeds") as set_motor_speeds_mock:
            # base case
            d.rotate(angle=90, time_to_take=1)
            set_motor_speeds_mock.assert_called_once_with(
                -0.12801990063378407, 0.12801990063378407, distance=0.12801990063378407
            )
            sleep_mock.assert_called_once_with(1)
            set_motor_speeds_mock.reset_mock()
            sleep_mock.reset_mock()

            # using a higher speed factor with the same time to take doesn't affect speeds
            d.rotate(angle=90, time_to_take=1, max_speed_factor=0.9)
            set_motor_speeds_mock.assert_called_once_with(
                -0.12801990063378407, 0.12801990063378407, distance=0.12801990063378407
            )
            sleep_mock.assert_called_once_with(1)
            sleep_mock.reset_mock()
            set_motor_speeds_mock.reset_mock()

            # using a lower speed factor with the same time to take will use lower speeds and will increase the time to take accordingly
            d.rotate(angle=90, time_to_take=1, max_speed_factor=0.1)
            set_motor_speeds_mock.assert_called_once_with(
                -0.044700000000000004,
                0.044700000000000004,
                distance=0.12801990063378407,
            )
            sleep_mock.assert_called_once_with(2.8639798799504264)
            sleep_mock.reset_mock()
            set_motor_speeds_mock.reset_mock()

            # using a small time to take with the default max speed factor will re-adjust the time to take
            d.rotate(angle=90, time_to_take=0.3)
            set_motor_speeds_mock.assert_called_once_with(
                -0.1341, 0.1341, distance=0.12801990063378407
            )
            sleep_mock.assert_called_once_with(0.9546599599834755)
            sleep_mock.reset_mock()
            set_motor_speeds_mock.reset_mock()

            # using a small time to take but increasing the max speed factor will achieve the expected time
            d.rotate(angle=90, time_to_take=0.3, max_speed_factor=1)
            set_motor_speeds_mock.assert_called_once_with(
                -0.4267330021126136, 0.4267330021126136, distance=0.12801990063378407
            )
            sleep_mock.assert_called_once_with(0.3)
            sleep_mock.reset_mock()
            set_motor_speeds_mock.reset_mock()
