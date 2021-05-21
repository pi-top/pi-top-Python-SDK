from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator
from pitop.pma import ServoMotor
from .pan_tilt_object_tracker import PanTiltObjectTracker


class PanTiltController(Stateful, Recreatable):
    CALIBRATION_FILE_NAME = "pan_tilt.conf"
    _pan_servo = None
    _tilt_servo = None

    def __init__(self, servo_pan_port="S0", servo_tilt_port="S3", name="pan_tilt"):
        self.name = name
        self._pan_servo = ServoMotor(servo_pan_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)

        self._object_tracker = PanTiltObjectTracker(pan_servo=self._pan_servo, tilt_servo=self._tilt_servo)

        Stateful.__init__(self, children=['_pan_servo', '_tilt_servo'])
        Recreatable.__init__(self, config_dict={'servo_pan_port': servo_pan_port, 'servo_tilt_port': servo_tilt_port,
                                                'name': name})

    @property
    def pan_servo(self):
        return self._pan_servo

    @property
    def tilt_servo(self):
        return self._tilt_servo

    @property
    def track_object(self) -> PanTiltObjectTracker:
        return self._object_tracker

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
            section_name="PAN_TILT",
            servo_lookup_dict={"pan_zero_point": self.pan_servo, "tilt_zero_point": self.tilt_servo}
        )
        calibration_object.calibrate(save, reset)
