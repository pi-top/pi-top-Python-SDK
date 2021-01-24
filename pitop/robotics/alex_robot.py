from pitop import PiTop
from pitop.camera import Camera
from pitop.pma import (
    UltrasonicSensor
)

from pitopcommon.common_ids import FirmwareDeviceID

from .drive_controller import DriveController
from .pan_tilt_controller import PanTiltController

import configparser
from os import mkdir
from os.path import (
    exists,
    isdir,
    join,
)
from pathlib import Path

from math import radians


class AlexRobot(PiTop):
    CALIBRATION_FILE_DIR = ".config/pi-top/sdk"
    CALIBRATION_FILE_NAME = "alex.conf"

    def __init__(self,
                 motor_left_port="M3",
                 motor_right_port="M0",
                 camera_id=0,
                 ultrasonic_sensor_port="D3",
                 servo_pan_port="S0",
                 servo_tilt_port="S3"
                 ):

        super().__init__()
        if self._plate is None or self._plate != FirmwareDeviceID.pt4_expansion_plate:
            raise Exception("Expansion Plate not connected")

        self.camera = Camera(camera_id)
        self.ultrasonic_sensor = UltrasonicSensor(ultrasonic_sensor_port)
        self.port_manager.register_component_instance(self.ultrasonic_sensor, ultrasonic_sensor_port)

        self._drive_controller = DriveController(motor_left_port, motor_right_port)
        self.left_motor = self.port_manager.get_component(motor_left_port)
        self.right_motor = self.port_manager.get_component(motor_right_port)

        self._pan_tilt_controller = PanTiltController(servo_pan_port=servo_pan_port, servo_tilt_port=servo_tilt_port)
        self.pan_servo = self.port_manager.get_component(servo_pan_port)
        self.tilt_servo = self.port_manager.get_component(servo_tilt_port)

        self.__calibration_file_path = join(str(Path.home()), self.CALIBRATION_FILE_DIR, self.CALIBRATION_FILE_NAME)

        self.__load_calibration()

    def forward(self, speed_factor, hold=False):
        self._drive_controller.forward(speed_factor, hold)

    def backward(self, speed_factor, hold=False):
        self._drive_controller.backward(speed_factor, hold)

    def left(self, speed_factor, turn_radius=0):
        self._drive_controller.left(speed_factor, turn_radius)

    def right(self, speed_factor, turn_radius=0):
        self._drive_controller.right(speed_factor, turn_radius)

    def rotate(self, angle, time_to_take):
        angle_radians = radians(angle)
        angular_speed = angle_radians / time_to_take
        self._drive_controller.rotate(angle, angular_speed)
        # TODO: shall we add a sleep here to make it blocking?
        #  Ideally we'd have it return properly when motors have finished turning

    def stop(self):
        self._drive_controller.stop()

    def target_lock_drive_angle(self, angle):
        self._drive_controller.target_lock_drive_angle(angle)

    def calibrate(self, save=True, reset=False):
        if not reset:
            return self.__load_calibration()

        # PanTilt servo calibration
        servo_lookup = {
            'pan_zero_point': self.pan_servo,
            'tilt_zero_point': self.tilt_servo,
        }
        for servo_name, servo_obj in servo_lookup.items():
            value = self.__calibrate_servo(servo_name, servo_obj)
            if save and value is not None:
                self.__save_calibration(section='PAN_TILT', values_dict={servo_name: value})

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
                    print(f"PanTilt.pan_servo.zero = {int(section_config.get('pan_zero_point'))}")
                    self.pan_servo.zero_point = int(section_config.get('pan_zero_point'))

                if section_config.get('tilt_zero_point'):
                    print(f"PanTilt.tilt_servo.zero = {int(section_config.get('tilt_zero_point'))}")
                    self.tilt_servo.zero_point = int(section_config.get('tilt_zero_point'))

    def __save_calibration(self, section, values_dict):
        def create_config_file():
            conf_file_dir = join(str(Path.home()), self.CALIBRATION_FILE_DIR)
            if not isdir(conf_file_dir):
                mkdir(conf_file_dir)
            if not exists(self.__calibration_file_path):
                Path.touch(self.__calibration_file_path)

        if not exists(self.__calibration_file_path):
            create_config_file()

        config = configparser.ConfigParser()
        config.read(self.__calibration_file_path)
        if section not in config:
            config[section] = {}

        config[section].update({k: str(v) for k, v in values_dict.items()})
        with open(self.__calibration_file_path, 'w') as configfile:
            config.write(configfile)

    def rotate(self, angle, angular_speed=2):
        self._drive_controller.rotate(angle, angular_speed)
