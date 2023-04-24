import time
from dataclasses import dataclass
from threading import Thread
from time import sleep
from typing import Optional

from pitop.core.mixins import Recreatable, Stateful
from pitop.pma import ServoMotor
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator

from .simple_pid import PID


@dataclass
class OscillateRequest:
    servo: ServoMotor
    times: int
    angle: int
    speed: int
    block: bool


class ThreadControl:
    def __init__(self):
        self.thread = Thread()
        self.cancel = False


class TiltRollHeadController(Stateful, Recreatable):
    CALIBRATION_FILE_NAME = "tilt_roll.conf"
    _roll_servo = None
    _tilt_servo = None

    def __init__(self, servo_roll_port="S0", servo_tilt_port="S3", name="head"):
        self.name = name
        self._roll_servo = ServoMotor(servo_roll_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)

        self._head_roll_pid = PID(
            Kp=3.0, Ki=1.5, Kd=0.25, setpoint=0, output_limits=(-100, 100)
        )

        self.timeout = 5  # s
        self.__shake_thread_control = ThreadControl()
        self.__nod_thread_control = ThreadControl()

        Stateful.__init__(self, children=["_roll_servo", "_tilt_servo"])
        Recreatable.__init__(
            self,
            config_dict={
                "servo_roll_port": servo_roll_port,
                "servo_tilt_port": servo_tilt_port,
                "name": name,
            },
        )

    @property
    def roll(self) -> ServoMotor:
        return self._roll_servo

    @property
    def tilt(self) -> ServoMotor:
        return self._tilt_servo

    def stop(self) -> None:
        self.tilt.sweep(speed=0)
        self.roll.sweep(speed=0)

    def shake(
        self, times: int = 4, angle: int = 5, speed: int = 100, block: bool = True
    ) -> None:
        """Shakes the head by rotating the roll servo back and forth between
        :data:`-angle` and :data:`+angle` from current angle position.

        :param int times: Number of times to shake head
        :param int angle: angle in degrees either side of current angle to rotate servo by
        :param int speed: servo speed in deg/s
        :param bool block: if `True`, function call will block program execution until finished
        :return: None
        """
        oscillate_request = OscillateRequest(
            servo=self._roll_servo, times=times, angle=angle, speed=speed, block=block
        )

        self.__start_servo_oscillation(
            oscillate_request, thread_control=self.__shake_thread_control
        )

    def nod(
        self, times: int = 4, angle: int = 5, speed: int = 100, block: bool = True
    ) -> None:
        """Nod the head by rotating the tilt servo back and forth between
        :data:`-angle` and :data:`+angle` from current angle position.

        :param int times: Number of times to nod head
        :param int angle: angle in degrees either side of current angle to rotate servo by
        :param int speed: servo speed in deg/s
        :param bool block: if `True`, function call will block program execution until finished
        :return: None
        """
        oscillate_request = OscillateRequest(
            servo=self._tilt_servo, times=times, angle=angle, speed=speed, block=block
        )

        self.__start_servo_oscillation(
            oscillate_request, thread_control=self.__nod_thread_control
        )

    def __start_servo_oscillation(
        self, oscillate_request: OscillateRequest, thread_control: ThreadControl
    ):
        if thread_control.thread.is_alive():
            thread_control.cancel = True
            thread_control.thread.join()
            thread_control.cancel = False

        if oscillate_request.block:
            self.__oscillate_servo(
                oscillate_request=oscillate_request, thread_control=thread_control
            )
        else:
            thread_control.thread = Thread(
                target=self.__oscillate_servo,
                kwargs={
                    "oscillate_request": oscillate_request,
                    "thread_control": thread_control,
                },
                daemon=True,
            )
            thread_control.thread.start()

    def __oscillate_servo(
        self, oscillate_request: OscillateRequest, thread_control: ThreadControl
    ) -> None:
        def reset_servo_state():
            oscillate_request.servo.target_speed = previous_target_speed
            self.__set_angle_until_reached(
                servo=oscillate_request.servo, angle=starting_angle
            )

        previous_target_speed = oscillate_request.servo.target_speed
        oscillate_request.servo.target_speed = oscillate_request.speed

        starting_angle = oscillate_request.servo.current_angle
        angle_start = starting_angle - oscillate_request.angle
        angle_end = starting_angle + oscillate_request.angle

        for _ in range(oscillate_request.times):
            if thread_control.cancel:
                reset_servo_state()
                return

            self.__set_angle_until_reached(
                servo=oscillate_request.servo,
                angle=angle_start,
                thread_control=thread_control,
            )
            self.__set_angle_until_reached(
                servo=oscillate_request.servo,
                angle=angle_end,
                thread_control=thread_control,
            )

        reset_servo_state()

    def __set_angle_until_reached(
        self,
        servo: ServoMotor,
        angle: int,
        thread_control: Optional[ThreadControl] = None,
    ):
        def cancelled():
            if time.time() - start_time > self.timeout:
                servo.stop()
                thread_control.cancel = True
                print(
                    f"Head nod/shake cancelled because time exceeded {self.timeout} seconds. Try a higher speed."
                )
                return True
            if thread_control is not None:
                return thread_control.cancel
            return False

        start_time = time.time()
        if not cancelled():
            servo.target_angle = angle

            while abs(angle - servo.current_angle) > 1:
                if cancelled():
                    break
                sleep(0.05)

    def track_head_angle(self, angle: int, flipped=True) -> None:
        if not flipped:
            angle = -angle
        current_angle = self.roll.current_angle
        error = current_angle - angle
        if abs(error) < 1.0:
            self.roll.sweep(speed=0)
        else:
            servo_speed = self._head_roll_pid(error)
            self.roll.sweep(speed=servo_speed)

    def calibrate(self, save: bool = True, reset: bool = False) -> None:
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
            servo_lookup_dict={
                "roll_zero_point": self.roll,
                "tilt_zero_point": self.tilt,
            },
        )
        calibration_object.calibrate(save, reset)
