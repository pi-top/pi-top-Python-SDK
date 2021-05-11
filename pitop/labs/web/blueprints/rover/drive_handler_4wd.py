from sched import scheduler
from threading import Thread
import time
from .helpers import calculate_direction
import math

MAX_LINEAR_SPEED = 0.596
MAX_ANGULAR_SPEED = 3.24


def calculate_joystick_vector(data):
    angle = data.get('angle', {})
    degree = angle.get('degree', 0)
    distance = data.get('distance', 0)
    direction = math.radians(calculate_direction(degree))

    return distance, direction


def calculate_linear_velocities(data):
    distance, direction = calculate_joystick_vector(data)
    linear_speed_x = (distance * MAX_LINEAR_SPEED / 100.0) * math.cos(direction)
    linear_speed_y = (distance * MAX_LINEAR_SPEED / 100.0) * math.sin(direction)

    return {
        'linear_speed_x': linear_speed_x,
        'linear_speed_y': linear_speed_y,
    }


def calculate_angular_velocity(data):
    distance, direction = calculate_joystick_vector(data)
    angular_speed_z = (distance * MAX_ANGULAR_SPEED / 100.0) * math.sin(direction)
    return {
        'angular_speed_z': angular_speed_z
    }


class DriveHandler4WD:
    def __init__(self, drive):
        self._drive = drive
        self._v_x = 0.0
        self._v_y = 0.0
        self._w_z = 0.0
        self._publish_dt = 1 / 10.0
        self._publish_thread = Thread(target=self.__publish_sheduler, daemon=True)
        self._publish_thread.start()

    def update_linear(self, data):
        linear_velocities = calculate_linear_velocities(data)
        self._v_x = linear_velocities.get('linear_speed_x', 0)
        self._v_y = linear_velocities.get('linear_speed_y', 0)

    def update_angular(self, data):
        angular_velocity = calculate_angular_velocity(data)
        self._w_z = angular_velocity.get('angular_speed_z', 0)

    def __publish_sheduler(self):
        s = scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(current_time + self._publish_dt, 1, self.__publish_velocity_commands, (s,))
        s.run()

    def __publish_velocity_commands(self, s):
        current_time = time.time()

        self._drive.robot_move(linear_x=self._v_x, linear_y=self._v_y, angular_z=self._w_z)

        s.enterabs(current_time + self._publish_dt, 1, self.__publish_velocity_commands, (s,))
