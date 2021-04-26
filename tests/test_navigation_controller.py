from sys import modules
from unittest.mock import Mock, MagicMock
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

from pitop.pma.encoder_motor import EncoderMotor
from pitop.pma.parameters import (
    ForwardDirection,
    Direction
)
from pitop.robotics.drive_controller import DriveController
from pitop.robotics.navigation.navigation_controller import NavigationController
import math


class EncoderMotorSim(EncoderMotor):
    _SPEED_NOISE_SIGMA_RATIO = 0.05

    def __init__(self, port_name, forward_direction):
        super().__init__(port_name=port_name, forward_direction=forward_direction)

        self._target_speed = 0.0
        self._current_speed = 0.0
        self._motor_speed_update_schedule = 1.0 / 20.0

    @property
    def current_speed(self):
        return self._target_speed

    def set_target_rpm(self, target_rpm, direction=Direction.FORWARD, total_rotations=0.0):
        self._target_speed = self._rpm_to_speed(target_rpm)

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self.wheel_circumference / 60.0, 3)
        return speed


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

    @staticmethod
    def get_navigation_controller():
        drive = DriveController()
        # over-ride motors
        drive.left_motor = EncoderMotorSim(port_name="M0",
                                           forward_direction=ForwardDirection.CLOCKWISE
                                           )
        drive.right_motor = EncoderMotorSim(port_name="M3",
                                            forward_direction=ForwardDirection.COUNTER_CLOCKWISE
                                            )
        return NavigationController(drive_controller=drive)

    def robot_state_assertions(self, navigation_controller, x_expected, y_expected, angle_expected):
        self.assertAlmostEqual(navigation_controller.robot_state.x, x_expected, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.y, y_expected, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.angle, angle_expected, delta=4)
        self.assertAlmostEqual(navigation_controller.robot_state.v, 0, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.w, 0, places=1)
