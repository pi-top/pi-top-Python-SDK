from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator
from pitop.pma import ServoMotor
from pitop.pma.servo_controller import ServoHardwareSpecs
from simple_pid import PID
from time import time


class PanTiltObjectTracker:
    _pid_tunings = {
        'slow': {"kp": 0.075, "ki": 0.002, "kd": 0.04},
        'normal': {"kp": 0.25, "ki": 0.005, "kd": 0.1}
    }
    _target_lock_range = 10
    _slow_fps_limit = 5.0

    def __init__(self, pan_servo, tilt_servo):
        self.__pan_servo = pan_servo
        self.__tilt_servo = tilt_servo
        self._previous_time = time()
        self.pan_pid = PID(setpoint=0,
                           output_limits=(-ServoHardwareSpecs.SPEED_RANGE, ServoHardwareSpecs.SPEED_RANGE))
        self.tilt_pid = PID(setpoint=0,
                            output_limits=(-ServoHardwareSpecs.SPEED_RANGE, ServoHardwareSpecs.SPEED_RANGE))
        self.__set_pid_tunings(pid_mode="normal")

    def __call__(self, center):
        current_time = time()
        if current_time - self._previous_time > 1 / self._slow_fps_limit:
            pid_mode = "slow"
        else:
            pid_mode = "normal"
        self._previous_time = current_time
        self.__set_pid_tunings(pid_mode=pid_mode)

        x, y = center

        # TODO: ideally would wait until servo speed changed direction before turning off PID.
        #  Currently, if object moves across center point during tracking the tracker will pause and
        #  reset before continuing
        if abs(x) < self._target_lock_range:
            self.__pan_servo.sweep(0)
            self.pan_pid.reset()
        else:
            pan_speed = self.pan_pid(x)
            self.__pan_servo.sweep(pan_speed)

        if abs(y) < self._target_lock_range:
            self.__tilt_servo.sweep(0)
            self.tilt_pid.reset()
        else:
            tilt_speed = self.tilt_pid(y)
            self.__tilt_servo.sweep(tilt_speed)

    def __set_pid_tunings(self, pid_mode):
        self.pan_pid.tunings = list(self._pid_tunings[pid_mode].values())
        self.tilt_pid.tunings = list(self._pid_tunings[pid_mode].values())

    def reset(self):
        self.pan_pid.reset()
        self.tilt_pid.reset()

    def stop(self):
        self.__pan_servo.sweep(0)
        self.__tilt_servo.sweep(0)
        self.reset()


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
