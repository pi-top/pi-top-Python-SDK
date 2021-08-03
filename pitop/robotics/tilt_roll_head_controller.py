from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import ServoMotor
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator
from .simple_pid import PID


class TiltRollHeadController(Stateful, Recreatable):
    CALIBRATION_FILE_NAME = "tilt_roll.conf"
    _roll_servo = None
    _tilt_servo = None

    def __init__(self, servo_roll_port="S0", servo_tilt_port="S3", name="head"):
        self.name = name
        self._roll_servo = ServoMotor(servo_roll_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)

        self._head_roll_pid = PID(Kp=3.0,
                                  Ki=1.5,
                                  Kd=0.25,
                                  setpoint=0,
                                  output_limits=(-100, 100)
                                  )

        Stateful.__init__(self, children=['_roll_servo', '_tilt_servo'])
        Recreatable.__init__(self, config_dict={'servo_roll_port': servo_roll_port, 'servo_tilt_port': servo_tilt_port, 'name': name})

    @property
    def roll(self):
        return self._roll_servo

    @property
    def tilt(self):
        return self._tilt_servo

    def stop(self):
        self.tilt.sweep(speed=0)
        self.roll.sweep(speed=0)

    def track_head_angle(self, angle, flipped=True):
        if not flipped:
            angle = -angle
        current_angle = self.roll.current_angle
        state = current_angle - angle
        if abs(state) < 1.0:
            self.roll.sweep(speed=0)
        else:
            servo_speed = self._head_roll_pid(state)
            self.roll.sweep(speed=servo_speed)

    def calibrate(self, save=True, reset=False):
        """Calibrates the assembly to work in optimal conditions.

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
        calibration_object = TwoServoAssemblyCalibrator(
            filename=self.CALIBRATION_FILE_NAME,
            section_name="TILT_ROLL",
            servo_lookup_dict={"roll_zero_point": self.roll, "tilt_zero_point": self.tilt}
        )
        calibration_object.calibrate(save, reset)
