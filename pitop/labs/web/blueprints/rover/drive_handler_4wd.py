from sched import scheduler
from threading import Thread
import time
from .helpers import calculate_direction
import math
from enum import IntEnum

MAX_LINEAR_SPEED = 0.596
MAX_ANGULAR_SPEED = 3.24
MAX_SERVO_ANGLE = 90.0


def get_joystick_distances(data):
    angle = data.get('angle', {})
    degree = angle.get('degree', 0)
    distance = data.get('distance', 0)
    direction = math.radians(calculate_direction(degree))

    horizontal_distance = distance * math.sin(direction) / 100.0
    vertical_distance = distance * math.cos(direction) / 100.0

    return horizontal_distance, vertical_distance


class DriveMode(IntEnum):
    FREE = 0  # pan servo is not controlled by web controller
    PAN_FOLLOW = 1  # pan servo is controlled by left joystick and chassis moves to follow it


class DriveHandler4WD:
    # TODO: investigate adding a timeout so robot stops if no new commands are sent after specified duration

    _MAX_PAN_ANGLE = 20
    _MAX_TILT_SERVO_SPEED = 50.0
    _JOYSTICK_DEADZONE = 0.05

    def __init__(self, drive, pan_tilt, mode: DriveMode = DriveMode.FREE):
        self._drive = drive
        self._pan_tilt = pan_tilt
        self._mode = mode
        self._linear_speed_x = 0.0
        self._linear_speed_y = 0.0
        self._angular_speed = 0.0
        self._pan_servo_angle = 0.0
        self._tilt_servo_speed = 0.0
        self._command_dt = 1 / 8.0
        self._command_thread = Thread(target=self.__command_scheduler, daemon=True)
        self._command_thread.start()

    def right_joystick_update(self, data):
        horiz_distance, vert_distance = get_joystick_distances(data)
        shifted_horiz_distance, shifted_vert_distance = self.__get_shifted_joystick_distances(
            horiz_distance, vert_distance)

        if abs(vert_distance) > self._JOYSTICK_DEADZONE:
            self._linear_speed_x = shifted_vert_distance * MAX_LINEAR_SPEED
        else:
            self._linear_speed_x = 0.0

        if abs(horiz_distance) > self._JOYSTICK_DEADZONE:
            self._linear_speed_y = shifted_horiz_distance * MAX_LINEAR_SPEED
        else:
            self._linear_speed_y = 0.0

    def left_joystick_update(self, data):
        horiz_distance, vert_distance = get_joystick_distances(data)
        shifted_horiz_distance, shifted_vert_distance = self.__get_shifted_joystick_distances(
            horiz_distance, vert_distance)

        if abs(vert_distance) > self._JOYSTICK_DEADZONE:
            self._tilt_servo_speed = -shifted_vert_distance * self._MAX_TILT_SERVO_SPEED
        else:
            self._tilt_servo_speed = 0.0

        if abs(horiz_distance) > self._JOYSTICK_DEADZONE:
            self._angular_speed = shifted_horiz_distance * MAX_ANGULAR_SPEED
            if self._mode == DriveMode.PAN_FOLLOW:
                self._pan_tilt.pan_servo.target_speed = 25.0  # set lower speed for turning angle
                pan_angle = shifted_horiz_distance * MAX_SERVO_ANGLE
                self._pan_servo_angle = max(-self._MAX_PAN_ANGLE, min(self._MAX_PAN_ANGLE, pan_angle))
        else:
            self._angular_speed = 0.0
            if self._mode == DriveMode.PAN_FOLLOW:
                self._pan_tilt.pan_servo.target_speed = 100.0  # set highest speed for reset back to zero
                self._pan_servo_angle = 0.0

    def __get_shifted_joystick_distances(self, horizontal_distance, vertical_distance):
        shifted_horiz_distance = horizontal_distance \
                                 - (self._JOYSTICK_DEADZONE * horizontal_distance / abs(horizontal_distance))
        shifted_vert_distance = vertical_distance \
                                - (self._JOYSTICK_DEADZONE * vertical_distance / abs(vertical_distance))

        return shifted_horiz_distance, shifted_vert_distance

    def __command_scheduler(self):
        s = scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(current_time + self._command_dt, 1, self.__command_loop, (s,))
        s.run()

    def __command_loop(self, s):
        current_time = time.time()

        self._drive.robot_move(linear_x=self._linear_speed_x,
                               linear_y=self._linear_speed_y,
                               angular_z=self._angular_speed
                               )
        self._pan_tilt.tilt_servo.sweep(speed=self._tilt_servo_speed)
        if self._mode == DriveMode.PAN_FOLLOW:
            self._pan_tilt.pan_servo.target_angle = self._pan_servo_angle

        s.enterabs(current_time + self._command_dt, 1, self.__command_loop, (s,))
