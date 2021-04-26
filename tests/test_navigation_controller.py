from sys import modules
from unittest.mock import Mock
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
from pitop import DriveController, NavigationController
from random import random, gauss, choice
from threading import Thread
import time
import sched
import math


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


class EncoderMotorSim(EncoderMotor):
    _SPEED_NOISE_SIGMA_RATIO = 0.05

    def __init__(self, port_name, forward_direction):
        super().__init__(port_name=port_name, forward_direction=forward_direction)

        self._target_speed = 0.0
        self._current_speed = 0.0
        self._motor_speed_update_schedule = 1.0 / 20.0
        self._motor_thread = Thread(target=self.__motor_speed_update_scheduler, daemon=True)
        self._motor_thread.start()

    @property
    def current_speed(self):
        return self._current_speed

    def set_target_rpm(self, target_rpm, direction=Direction.FORWARD, total_rotations=0.0):
        self._target_speed = self._rpm_to_speed(target_rpm)

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self.wheel_circumference / 60.0, 3)
        return speed

    def __motor_speed_update_scheduler(self):
        s = sched.scheduler(time.time, time.sleep)
        s.enter(self._motor_speed_update_schedule, 1, self.__update_motor_speed, (s, ))
        s.run()

    def __update_motor_speed(self, s):
        self._current_speed = gauss(
            mu=self._target_speed, sigma=self._target_speed * self._SPEED_NOISE_SIGMA_RATIO
        ) if self._target_speed is not 0 else 0

        s.enter(self._motor_speed_update_schedule, 1, self.__update_motor_speed, (s, ))


class DriveControllerSim(DriveController):
    def __init__(self, left_motor_port="M3", right_motor_port="M0"):
        super().__init__(left_motor_port=left_motor_port, right_motor_port=right_motor_port)

        # over-ride motors
        self.left_motor = EncoderMotorSim(port_name=self.left_motor_port,
                                          forward_direction=ForwardDirection.CLOCKWISE
                                          )
        self.right_motor = EncoderMotorSim(port_name=self.right_motor_port,
                                           forward_direction=ForwardDirection.COUNTER_CLOCKWISE
                                           )


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
        return NavigationController(drive_controller=DriveControllerSim(left_motor_port="M3", right_motor_port="M0"))

    def robot_state_assertions(self, navigation_controller, x_expected, y_expected, angle_expected):
        self.assertAlmostEqual(navigation_controller.robot_state.x, x_expected, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.y, y_expected, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.angle, angle_expected, delta=4)
        self.assertAlmostEqual(navigation_controller.robot_state.v, 0, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.w, 0, places=1)
