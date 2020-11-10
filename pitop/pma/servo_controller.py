from numpy import interp
from typing import Union

from pitop.utils.bitwise_ops import split_into_bytes
from .plate_interface import PlateInterface
from .common import type_check
from .common.servo_motor_registers import (
    ServoRegisterTypes,
    ServoControlRegisters,
    ServoControlModes,
    ServoMotorSetup)


class ServoHardwareSpecs:
    PWM_FREQUENCY = 60
    ANGLE_RANGE = 180
    SPEED_RANGE = 100
    MIN_PULSE_WIDTH_MICRO_S = 500
    MAX_PULSE_WIDTH_MICRO_S = 2500
    DUTY_REGISTER_RANGE = 4095


class ServoController:
    """
    Class used to read/write servo motor registers from the MCU
    """

    __lower_duty_cycle = 0
    __upper_duty_cycle = 0

    def __init__(self, port: str):
        if port not in ServoControlRegisters.__members__:
            raise Exception("Invalid port. Servo motors must be connected to ports S1-S4")

        self.registers = ServoControlRegisters[port].value
        self._mcu_device = PlateInterface.instance().get_device_mcu()

        self.set_pwm_frequency(ServoHardwareSpecs.PWM_FREQUENCY)
        self.set_min_pulse_width(ServoHardwareSpecs.MIN_PULSE_WIDTH_MICRO_S)
        self.set_max_pulse_width(ServoHardwareSpecs.MAX_PULSE_WIDTH_MICRO_S)

    @type_check
    def set_min_pulse_width(self, min_width_us: int) -> None:
        self._mcu_device.write_word(ServoMotorSetup.REGISTER_MIN_PULSE_WIDTH,
                                    min_width_us,
                                    signed=False,
                                    little_endian=True)

        self.__lower_duty_cycle = ServoHardwareSpecs.DUTY_REGISTER_RANGE * ((min_width_us * 1e-6) * self.pwm_frequency())
        self.__lower_duty_cycle = int(round(self.__lower_duty_cycle))

    @type_check
    def set_max_pulse_width(self, max_width_us: int) -> None:
        self._mcu_device.write_word(ServoMotorSetup.REGISTER_MAX_PULSE_WIDTH,
                                    max_width_us,
                                    signed=False,
                                    little_endian=True)

        self.__upper_duty_cycle = ServoHardwareSpecs.DUTY_REGISTER_RANGE * ((max_width_us * 1e-6) * self.pwm_frequency())
        self.__upper_duty_cycle = int(round(self.__upper_duty_cycle))

    @type_check
    def set_pwm_frequency(self, frequency: int) -> None:
        self._mcu_device.write_byte(ServoMotorSetup.REGISTER_PWM_FREQUENCY, frequency)

    def pwm_frequency(self) -> int:
        return self._mcu_device.read_unsigned_byte(ServoMotorSetup.REGISTER_PWM_FREQUENCY)

    def get_target_angle(self) -> int:
        if self.control_mode() != ServoControlModes.MODE_1:
            return None

        duty_cycle = self._mcu_device.read_signed_word(
            self.registers[ServoRegisterTypes.ANGLE_AND_SPEED], little_endian=True)

        angle = interp(duty_cycle,
                       [self.__lower_duty_cycle, self.__upper_duty_cycle],
                       [-ServoHardwareSpecs.ANGLE_RANGE / 2, ServoHardwareSpecs.ANGLE_RANGE / 2])
        return int(round(angle))

    @type_check
    def set_target_angle(self, angle: Union[int, float], speed: Union[int, float] = 50.0):
        mapped_duty_cycle = interp(angle,
                                   [-ServoHardwareSpecs.ANGLE_RANGE / 2, ServoHardwareSpecs.ANGLE_RANGE / 2],
                                   [self.__lower_duty_cycle, self.__upper_duty_cycle])
        mapped_duty_cycle = int(round(mapped_duty_cycle))

        mapped_speed = int(round(speed * 10))

        self.set_control_mode(ServoControlModes.MODE_1)

        list_to_send = split_into_bytes(mapped_duty_cycle, 2, signed=True, little_endian=True)
        list_to_send += split_into_bytes(mapped_speed, 2, signed=True, little_endian=True)

        self._mcu_device.write_n_bytes(self.registers[ServoRegisterTypes.ANGLE_AND_SPEED], list_to_send)

    def get_target_speed(self) -> float:
        if self.control_mode() != ServoControlModes.MODE_0:
            return None
        speed = self._mcu_device.read_signed_word(self.registers[ServoRegisterTypes.SPEED], little_endian=True)
        return round(speed / 10, 1)

    @type_check
    def set_target_speed(self, speed: Union[int, float]):
        if not (-ServoHardwareSpecs.SPEED_RANGE <= speed <= ServoHardwareSpecs.SPEED_RANGE):
            raise ValueError(f"Servo speed must be between -{ServoHardwareSpecs.SPEED_RANGE} and"
                             f"{ServoHardwareSpecs.SPEED_RANGE}")

        speed = round(speed * 10, 1)
        self.set_control_mode(ServoControlModes.MODE_0)
        self._mcu_device.write_word(self.registers[ServoRegisterTypes.SPEED],
                                    speed,
                                    little_endian=True,
                                    signed=True)

    @type_check
    def set_control_mode(self, control_mode: ServoControlModes):
        self._mcu_device.write_byte(self.registers[ServoRegisterTypes.CONTROL_MODE], control_mode.value)

    def control_mode(self) -> ServoControlModes:
        reported_control_mode = self._mcu_device.read_unsigned_byte(self.registers[ServoRegisterTypes.CONTROL_MODE])
        return ServoControlModes(reported_control_mode)
