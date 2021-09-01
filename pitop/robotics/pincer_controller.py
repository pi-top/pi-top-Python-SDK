from pitop.core.mixins import Recreatable, Stateful
from pitop.pma import ServoMotor, ServoMotorSetting
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator


class PincerController(Stateful, Recreatable):
    """Represents a pincer that uses two servo motors connected parallel to
    each other."""

    CALIBRATION_FILE_NAME = "pincers.conf"
    _left_pincer = None
    _right_pincer = None

    def __init__(self, left_pincer_port="S3", right_pincer_port="S0", name="pincers"):
        self.name = name
        self._left_pincer = ServoMotor(left_pincer_port)
        self._right_pincer = ServoMotor(right_pincer_port)
        self.__left_pincer_setting = ServoMotorSetting()
        self.__right_pincer_setting = ServoMotorSetting()

        Stateful.__init__(self, children=["_left_pincer", "_right_pincer"])
        Recreatable.__init__(
            self,
            config_dict={
                "left_pincer_port": left_pincer_port,
                "right_pincer_port": right_pincer_port,
                "name": self.name,
            },
        )

    def close(self, speed: int = 100, angle: int = 0):
        self.__left_pincer_setting.speed = speed
        self.__left_pincer_setting.angle = angle

        self.__right_pincer_setting.speed = speed
        self.__right_pincer_setting.angle = -angle

        self.pincer_move(
            left_servo_setting=self.__left_pincer_setting,
            right_servo_setting=self.__right_pincer_setting,
        )

    def open(self, speed: int = 50, angle: int = 45):
        self.__left_pincer_setting.speed = speed
        self.__left_pincer_setting.angle = -angle

        self.__right_pincer_setting.speed = speed
        self.__right_pincer_setting.angle = angle

        self.pincer_move(
            left_servo_setting=self.__left_pincer_setting,
            right_servo_setting=self.__right_pincer_setting,
        )

    def pincer_move(self, left_servo_setting, right_servo_setting):
        self._left_pincer.setting = left_servo_setting
        self._right_pincer.setting = right_servo_setting

    def calibrate(self, save=True, reset=False):
        """Calibrates the assembly to work in optimal conditions. Based on the
        provided arguments, it will either load the calibration values stored
        in the pi-top, or it will run the calibration process, requesting the
        user input in an interactive fashion.

        :param bool reset:
            If `true`, the existing calibration values will be reset, and the calibration process will be started.
            If set to `false`, the calibration values will be retrieved from the calibration file.
        :param bool save:
            If `reset` is `true`, this parameter will cause the calibration values to be stored to the calibration file if set to `true`.
            If `save=False`, the calibration values will only be used for the current session.
        """
        calibration_object = TwoServoAssemblyCalibrator(
            filename=self.CALIBRATION_FILE_NAME,
            section_name="PINCERS",
            servo_lookup_dict={
                "left_pincer_zero_point": self._left_pincer,
                "right_pincer_zero_point": self._right_pincer,
            },
        )
        calibration_object.calibrate(save, reset)
