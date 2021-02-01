from pitop import PiTop
from pitop.camera import Camera
from pitop.pma import UltrasonicSensor

from pitopcommon.common_ids import FirmwareDeviceID

from .drive_controller import DriveController
from .pan_tilt_controller import PanTiltController

import configparser
from math import radians
from os.path import (
    exists,
    isdir,
    join,
)
from pathlib import Path
from time import sleep


class AlexRobot(PiTop):
    """
    Abstraction of a pi-top [4] and Robotics Kit, assembled in an 'Alex' configuration.

    Inherits from :class:`PiTop`: all methods, attributes and properties from that
    class are also available through an `AlexRobot` object. This class builds on top of
    :class:`PiTop` to make available to the user all the methods to move the robot and
    to interact with all the features available in a pi-top [4].

    :param int camera_device_index: ID of the video capturing device to open. To open the default camera, use 0.
    :param tuple camera_resolution: Tuple with the camera resolution, as (width, height). Defaults to (640, 480).
    :param str ultrasonic_sensor_port: Port where the ultrasonic sensor is connected.
    :param str motor_left_port: Port where the left wheel motor is connected.
    :param str motor_right_port: Port where the right wheel motor is connected.
    :param str servo_pan_port: Port where the servo motor used to pan the camera is connected.
    :param int servo_tilt_port: Port where the servo motor used to tilt the camera is connected.

    """
    CALIBRATION_FILE_DIR = ".config/pi-top/sdk"
    CALIBRATION_FILE_NAME = "alex.conf"

    def __init__(self,
                 camera_device_index=0,
                 camera_resolution=(640, 480),
                 ultrasonic_sensor_port="D3",
                 motor_left_port="M3",
                 motor_right_port="M0",
                 servo_pan_port="S0",
                 servo_tilt_port="S3",
                 ):
        super().__init__()
        if self._plate is None or self._plate != FirmwareDeviceID.pt4_expansion_plate:
            raise Exception("Expansion Plate not connected")

        self.camera = Camera(camera_device_index, camera_resolution)
        self.ultrasonic_sensor = UltrasonicSensor(ultrasonic_sensor_port)
        self.register_pma_component(self.ultrasonic_sensor)

        self._drive_controller = DriveController(motor_left_port, motor_right_port)
        self.left_motor = self.get_component_on_pma_port(motor_left_port)
        self.right_motor = self.get_component_on_pma_port(motor_right_port)

        self._pan_tilt_controller = PanTiltController(servo_pan_port=servo_pan_port, servo_tilt_port=servo_tilt_port)
        self.pan_servo = self.get_component_on_pma_port(servo_pan_port)
        self.tilt_servo = self.get_component_on_pma_port(servo_tilt_port)

        self.__calibration_file_path = join(str(Path.home()), self.CALIBRATION_FILE_DIR, self.CALIBRATION_FILE_NAME)

    def forward(self, speed_factor, hold=False):
        """
        Move the robot forward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move backwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        self._drive_controller.forward(speed_factor, hold)

    def backward(self, speed_factor, hold=False):
        """
        Move the robot backward.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to move forwards.
        :param bool hold:
            Setting this parameter to true will cause subsequent movements to use the speed set as the base speed.
        """
        self._drive_controller.backward(speed_factor, hold)

    def left(self, speed_factor, turn_radius=0):
        """
        Make the robot move to the left, using a circular trajectory.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn right.
        :param float turn_radius:
            Radius used by the robot to perform the movement. Using `turn_radius=0` will cause the robot to rotate in place.
        """
        self._drive_controller.left(speed_factor, turn_radius)

    def right(self, speed_factor, turn_radius=0):
        """
        Make the robot move to the right, using a circular trajectory.

        :param float speed_factor:
            Factor relative to the maximum motor speed, used to set the velocity, in the range -1.0 to 1.0.
            Using negative values will cause the robot to turn left.
        :param float turn_radius:
            Radius used by the robot to perform the movement. Using `turn_radius=0` will cause the robot to rotate in place.
        """
        self._drive_controller.right(speed_factor, turn_radius)

    def rotate(self, angle, time_to_take):
        """
        Rotate the robot in place by a given angle and stop.

        :param float angle: Angle of the turn.
        :param float time_to_take: Expected duration of the rotation, in seconds.
        """
        assert time_to_take > 0.0
        angle_radians = radians(angle)
        angular_speed = angle_radians / time_to_take
        self._drive_controller.rotate(angle, angular_speed)
        sleep(time_to_take)

    def stop_rotation(self):
        """
        Stops any angular movement performed by the robot.

        In the case where linear and rotational movements are being performed at
        the same time (e.g.: during a left turn with a turn radius different to 0),
        calling this method will cause the robot to continue the linear movement,
        so it will continue to move forward.
        """
        self._drive_controller.stop_rotation()

    def stop(self):
        """
        Completely stops the robot.
        """
        self._drive_controller.stop()

    def target_lock_drive_angle(self, angle):
        self._drive_controller.target_lock_drive_angle(angle)

    def calibrate(self, save=True, reset=False):
        """
        Calibrates the robot to work in optimal conditions.

        Based on the provided arguments, it will either load the calibration
        values stored in the pi-top, or it will run the calibration process,
        requesting the user input in an interactive fashion.

        :param bool reset:
            If `true`, the existing calibration values will be reset, and the calibration process will be started.
            If set to `false`, the calibration values will be retrieved from the calibration file.
        :param bool save:
            If `reset` is `true`, this parameter will cause the calibration values to be stored to the calibration file if set to `true`.
            If `save=False`, the calibration values will only be used for the current session.
        """
        if not reset and exists(self.__calibration_file_path):
            return self.__load_calibration()

        # PanTilt servo calibration
        self.pan_servo.zero_point = 0
        self.tilt_servo.zero_point = 0
        servo_lookup = {
            'pan_zero_point': self.pan_servo,
            'tilt_zero_point': self.tilt_servo,
        }
        for servo_name, servo_obj in servo_lookup.items():
            value = self.__calibrate_servo(servo_name, servo_obj)
            if save and value is not None:
                self.__save_calibration(section='PAN_TILT', values_dict={servo_name: value})

        print("Calibration finished.")

    def __calibrate_servo(self, servo_name, servo_obj):
        print(f"Starting {servo_name} servo motor calibration.")

        while True:
            servo_obj.target_angle = 0
            print("Enter a angle to use as zero point.")
            user_zero_setting = input("Value: ")
            try:
                user_zero_setting = int(user_zero_setting)
                if user_zero_setting < int(servo_obj.angle_range[0]) or user_zero_setting > int(servo_obj.angle_range[1]):
                    print(f"Invalid angle value {user_zero_setting}. "
                          f" Please enter a value in the range {servo_obj.angle_range}")
                    continue
            except ValueError:
                print("Please, enter a valid value")
                continue

            servo_obj.target_angle = user_zero_setting

            print("Is the servo horn aligned with the body?")
            finished_calibration = str(input("'y' to accept, 'n' to try again, 'e' to exit: "))
            if finished_calibration.upper() == 'Y':
                servo_obj.zero_point = user_zero_setting
                return user_zero_setting
            elif finished_calibration.upper() == 'E':
                return None

    def __load_calibration(self):
        if exists(self.__calibration_file_path):
            config = configparser.ConfigParser()
            config.read(self.__calibration_file_path)

            if 'PAN_TILT' in config.sections():
                section_config = config['PAN_TILT']
                if section_config.get('pan_zero_point'):
                    # print(f"PanTilt.pan_servo.zero = {int(section_config.get('pan_zero_point'))}")
                    self.pan_servo.zero_point = int(section_config.get('pan_zero_point'))

                if section_config.get('tilt_zero_point'):
                    # print(f"PanTilt.tilt_servo.zero = {int(section_config.get('tilt_zero_point'))}")
                    self.tilt_servo.zero_point = int(section_config.get('tilt_zero_point'))

    def __save_calibration(self, section, values_dict):
        def create_config_file():
            conf_file_dir = join(str(Path.home()), self.CALIBRATION_FILE_DIR)
            if not isdir(conf_file_dir):
                Path(conf_file_dir).mkdir(parents=True, exist_ok=True)
            if not exists(self.__calibration_file_path):
                Path(self.__calibration_file_path).touch()

        if not exists(self.__calibration_file_path):
            create_config_file()

        config = configparser.ConfigParser()
        config.read(self.__calibration_file_path)
        if section not in config:
            config[section] = {}

        config[section].update({k: str(v) for k, v in values_dict.items()})
        with open(self.__calibration_file_path, 'w') as configfile:
            config.write(configfile)
