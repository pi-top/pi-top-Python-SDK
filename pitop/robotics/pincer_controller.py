from pitop.pma import ServoMotor, ServoMotorSetting
from pitop.core.exceptions import UninitializedComponent
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)


class PincerController(Stateful, Recreatable):
    """Represents a pincer that uses two servo motors connected parallel to
    each other."""
    _initialized = False

    def __init__(self, right_pincer_port="S0", left_pincer_port="S3", name="pincers"):
        self.name = name
        self._right_pincer = ServoMotor(right_pincer_port)
        self._left_pincer = ServoMotor(left_pincer_port)
        self.__right_pincer_setting = ServoMotorSetting()
        self.__left_pincer_setting = ServoMotorSetting()

        Stateful.__init__(self, children=['left_pincer', 'right_pincer'])
        Recreatable.__init__(self,
                             config_dict={"left_pincer_port": left_pincer_port, "right_pincer_port": right_pincer_port,
                                          "name": self.name})

    def is_initialized(fcn):
        def check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise UninitializedComponent("PincerController not initialized")
            return fcn(self, *args, **kwargs)
        return check_initialization

    @is_initialized
    def close(self, speed: int = 100, angle: int = 0):
        self.__right_pincer_setting.speed = speed
        self.__right_pincer_setting.angle = angle
        self.__left_pincer_setting.speed = speed
        self.__left_pincer_setting.angle = angle
        self._right_pincer.setting = self.__right_pincer_setting
        self._left_pincer.setting = self.__left_pincer_setting

    @is_initialized
    def open(self, speed: int = 50, angle: int = 45):
        self.__right_pincer_setting.speed = speed
        self.__right_pincer_setting.angle = angle
        self.__left_pincer_setting.speed = speed
        self.__left_pincer_setting.angle = -angle
        self._right_pincer.setting = self.__right_pincer_setting
        self._left_pincer.setting = self.__left_pincer_setting
