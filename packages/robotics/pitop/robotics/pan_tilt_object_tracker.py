from time import time

from pitop.pma.servo_controller import ServoHardwareSpecs

from .simple_pid import PID


class PanTiltObjectTracker:
    _pid_tunings = {
        "slow": {"kp": 0.075, "ki": 0.002, "kd": 0.04},
        "normal": {"kp": 0.25, "ki": 0.005, "kd": 0.1},
    }
    _target_lock_range = 10
    _slow_fps_limit = 5.0

    def __init__(self, pan_servo, tilt_servo):
        self.__pan_servo = pan_servo
        self.__tilt_servo = tilt_servo
        self._previous_time = time()
        self.pan_pid = PID(
            setpoint=0,
            output_limits=(
                -ServoHardwareSpecs.SPEED_RANGE,
                ServoHardwareSpecs.SPEED_RANGE,
            ),
        )
        self.tilt_pid = PID(
            setpoint=0,
            output_limits=(
                -ServoHardwareSpecs.SPEED_RANGE,
                ServoHardwareSpecs.SPEED_RANGE,
            ),
        )
        self.__set_pid_tunings(pid_mode="normal")

    def __call__(self, center):
        current_time = time()
        dt = current_time - self._previous_time
        if dt > 1 / self._slow_fps_limit:
            pid_mode = "slow"
        else:
            pid_mode = "normal"
        self._previous_time = current_time
        self.__set_pid_tunings(pid_mode=pid_mode)

        x, y = center

        if abs(x) < self._target_lock_range:
            self.__pan_servo.sweep(speed=0)
            self.pan_pid.reset()
        else:
            pan_speed = self.pan_pid(x)
            self.__pan_servo.sweep(pan_speed)

        if abs(y) < self._target_lock_range:
            self.__tilt_servo.sweep(speed=0)
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
