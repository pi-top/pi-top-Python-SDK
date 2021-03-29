from pitop.core.exceptions import UninitializedComponent
from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import ServoMotor


class TiltRollController(Stateful, Recreatable):
    _initialized = False
    _roll_servo = None
    _tilt_servo = None

    def __init__(self, servo_roll_port="S0", servo_tilt_port="S3", name="pan_tilt"):
        self.name = name
        self._roll_servo = ServoMotor(servo_roll_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)
        self._initialized = True

        Stateful.__init__(self, children=['_roll_servo', '_tilt_servo'])
        Recreatable.__init__(self, config_dict={'servo_roll_port': servo_roll_port, 'servo_tilt_port': servo_tilt_port, 'name': name})

    def is_initialized(fcn):
        def check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise UninitializedComponent("TiltRollController not initialized")
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
