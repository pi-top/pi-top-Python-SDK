from pitop.core.mixins import (
    Stateful,
    Recreatable,
)
from pitop.pma import ServoMotor
from pitop.robotics.two_servo_assembly_calibrator import TwoServoAssemblyCalibrator
from simple_pid import PID
from threading import Thread
from time import sleep


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

        self.__oscillate_thread = Thread()
        self.__new_request_received = False

        Stateful.__init__(self, children=['_roll_servo', '_tilt_servo'])
        Recreatable.__init__(self, config_dict={'servo_roll_port': servo_roll_port,
                                                'servo_tilt_port': servo_tilt_port,
                                                'name': name}
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

    def shake(self, times: int = 4, angle: int = 5, speed: int = 100, block: bool = True) -> None:
        """Shakes the head by rotating the roll servo back and forth between
        :data:`-angle` and :data:`+angle` from current angle position.

        :param int times: Number of times to shake head
        :param int angle: angle in degrees either side of current angle to rotate servo by
        :param int speed: servo speed in deg/s
        :param bool block: if `True`, function call will block program execution until finished
        :return: None
        """
        self.__start_servo_oscillation(servo=self._roll_servo, times=times, angle=angle, speed=speed, block=block)

    def nod(self, times: int = 4, angle: int = 5, speed: int = 100, block: bool = True) -> None:
        """Nod the head by rotating the tilt servo back and forth between
        :data:`-angle` and :data:`+angle` from current angle position.

        :param int times: Number of times to nod head
        :param int angle: angle in degrees either side of current angle to rotate servo by
        :param int speed: servo speed in deg/s
        :param bool block: if `True`, function call will block program execution until finished
        :return: None
        """
        self.__start_servo_oscillation(servo=self._tilt_servo, times=times, angle=angle, speed=speed, block=block)

    def __start_servo_oscillation(self, servo: ServoMotor, times: int, angle: int, speed: int, block: bool) -> None:
        if self.__oscillate_thread.is_alive():
            self.__new_request_received = True
            self.__oscillate_thread.join()
            self.__new_request_received = False
        if block:
            self.__oscillate_servo(servo=servo, times=times, angle=angle, speed=speed)
        else:
            self.__oscillate_thread = Thread(target=self.__oscillate_servo,
                                             kwargs={"servo": servo, "times": times, "angle": angle, "speed": speed},
                                             daemon=True)
            self.__oscillate_thread.start()

    def __oscillate_servo(self, servo: ServoMotor, times: int, angle: int, speed: int) -> None:
        def reset():
            servo.target_angle = starting_angle
            servo.target_speed = previous_target_speed

        previous_target_speed = servo.target_speed
        servo.target_speed = speed

        starting_angle = servo.current_angle
        shake_angle_start = starting_angle - angle
        shake_angle_end = starting_angle + angle

        for _ in range(times):
            if self.__new_request_received:
                reset()
                return
            self.__set_angle_until_reached(servo=servo, angle=shake_angle_start)
            self.__set_angle_until_reached(servo=servo, angle=shake_angle_end)

        # Reset the servo state to how it was before
        reset()

    def __set_angle_until_reached(self, servo: ServoMotor, angle):
        servo.target_angle = angle
        while abs(angle - servo.current_angle) > 1 and not self.__new_request_received:
            sleep(0.05)

    def track_head_angle(self, angle, flipped=True) -> None:
        if not flipped:
            angle = -angle
        current_angle = self.roll.current_angle
        error = current_angle - angle
        if abs(error) < 1.0:
            self.roll.sweep(speed=0)
        else:
            servo_speed = self._head_roll_pid(error)
            self.roll.sweep(speed=servo_speed)

    def calibrate(self, save=True, reset=False) -> None:
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
