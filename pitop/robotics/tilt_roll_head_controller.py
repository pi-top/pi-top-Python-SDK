import configparser
from os.path import (
    exists,
    isdir,
    join,
)
from pathlib import Path

from pitop.core.exceptions import UninitializedComponent
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import ServoMotor
from simple_pid import PID


class TiltRollHeadController(Stateful, Recreatable):
    CALIBRATION_FILE_DIR = ".config/pi-top/sdk"
    CALIBRATION_FILE_NAME = "prax.conf"
    _initialized = False
    _roll_servo = None
    _tilt_servo = None

    def __init__(self, servo_roll_port="S0", servo_tilt_port="S3", name="tilt_roll"):
        self.name = name
        self._roll_servo = ServoMotor(servo_roll_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)
        self.__calibration_file_path = join(str(Path.home()), self.CALIBRATION_FILE_DIR, self.CALIBRATION_FILE_NAME)
        self._initialized = True

        self._head_roll_pid = PID(Kp=3.0,
                                  Ki=1.5,
                                  Kd=0.25,
                                  setpoint=0,
                                  output_limits=(-100, 100)
                                  )

        Stateful.__init__(self, children=['_roll_servo', '_tilt_servo'])
        Recreatable.__init__(self, config_dict={'servo_roll_port': servo_roll_port, 'servo_tilt_port': servo_tilt_port, 'name': name})

    def is_initialized(fcn):
        def check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise UninitializedComponent("TiltRollHeadController not initialized")
            return fcn(self, *args, **kwargs)
        return check_initialization

    @property
    @is_initialized
    def roll_servo(self):
        return self._roll_servo

    @property
    @is_initialized
    def tilt_servo(self):
        return self._tilt_servo

    def stop(self):
        self.tilt_servo.sweep(speed=0)
        self.roll_servo.sweep(speed=0)

    def track_head_angle(self, angle, flipped=True):
        if not flipped:
            angle = -angle
        current_angle = self.roll_servo.current_angle
        state = current_angle - angle
        if abs(state) < 1.0:
            self.roll_servo.sweep(speed=0)
        else:
            servo_speed = self._head_roll_pid(state)
            self.roll_servo.sweep(speed=servo_speed)

    @is_initialized
    def calibrate(self, save=True, reset=False):
        """Calibrates the robot to work in optimal conditions.

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

        # TiltRoll servo calibration
        self.roll_servo.zero_point = 0
        self.tilt_servo.zero_point = 0
        servo_lookup = {
            'roll_zero_point': self.roll_servo,
            'tilt_zero_point': self.tilt_servo,
        }
        for servo_name, servo_obj in servo_lookup.items():
            value = self.__calibrate_servo(servo_name, servo_obj)
            if save and value is not None:
                self.__save_calibration(section='TILT_ROLL', values_dict={servo_name: value})

        print("Calibration finished.")

    def __calibrate_servo(self, servo_name, servo_obj):
        print(f"Starting {servo_name} servo motor calibration.")

        while True:
            servo_obj.target_angle = 0
            print("Enter a angle to use as zero point.")
            user_zero_setting = input("Value: ")
            try:
                user_zero_setting = int(user_zero_setting)
                if user_zero_setting < int(servo_obj.angle_range[0]) or user_zero_setting > int(
                        servo_obj.angle_range[1]):
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

            if 'TILT_ROLL' in config.sections():
                section_config = config['TILT_ROLL']
                if section_config.get('roll_zero_point'):
                    # print(f"PanTilt.pan_servo.zero = {int(section_config.get('pan_zero_point'))}")
                    self.roll_servo.zero_point = int(section_config.get('roll_zero_point'))

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
