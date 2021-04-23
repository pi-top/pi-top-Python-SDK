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

# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]

# drive_controller used: stop(), max_motor_speed(), robot_move(), motor_current_speeds

from pitop import DriveController, NavigationController
import random
from threading import Thread
import time
import sched


class EncoderMotorSim(EncoderMotor):
    def __init__(self, port_name, forward_direction):
        super().__init__(port_name=port_name, forward_direction=forward_direction)

        self._target_speed = 0.0
        self._current_speed = 0.0
        self._motor_speed_update_schedule = 1.0 / 20.0
        self._motor_thread = Thread(target=self.__motor_speed_thread_scheduler, daemon=True)
        self._motor_thread.start()

    @property
    def current_speed(self):
        return self._current_speed

    def set_target_rpm(self, target_rpm, direction=Direction.FORWARD, total_rotations=0.0):
        self._target_speed = self._rpm_to_speed(target_rpm)

    def _rpm_to_speed(self, rpm):
        speed = round(rpm * self.wheel_circumference / 60.0, 3)
        return speed

    def __motor_speed_thread_scheduler(self):
        s = sched.scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(current_time + self._motor_speed_update_schedule, 1, self.__update_motor_speed, (s, ))
        s.run()

    def __update_motor_speed(self, s):
        current_time = time.time()
        self._current_speed = random.gauss(mu=self._target_speed, sigma=self._target_speed * 0.01)
        s.enterabs(current_time + self._motor_speed_update_schedule, 1, self.__update_motor_speed, (s, ))


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

    def test_navigate_to_position(self):
        navigation_controller = NavigationController(
            drive_controller=DriveControllerSim(left_motor_port="M3", right_motor_port="M0")
        )
        x_goal = 0.25
        y_goal = 0.25
        angle_goal = 0
        navigation_controller.go_to(position=(x_goal, y_goal), angle=angle_goal).wait()

        self.assertAlmostEqual(navigation_controller.robot_state.x, x_goal, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.y, y_goal, places=1)
        self.assertAlmostEqual(navigation_controller.robot_state.angle, angle_goal, delta=2)
