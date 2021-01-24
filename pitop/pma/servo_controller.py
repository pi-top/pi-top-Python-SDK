from numpy import interp
from typing import Union

from pitopcommon.bitwise_ops import split_into_bytes
from .plate_interface import PlateInterface
from .common import type_check
from .common.servo_motor_registers import (
    ServoRegisterTypes,
    ServoControlRegisters,
    ServoMotorSetup)


class ServoHardwareSpecs:
    PWM_FREQUENCY = 60
    ANGLE_RANGE = 180
    SPEED_RANGE = 100
    MIN_PULSE_WIDTH_MICRO_S = 911
    MAX_PULSE_WIDTH_MICRO_S = 2165
    DUTY_REGISTER_RANGE = 4095


class ServoController:
    """
    Class used to read/write servo motor registers from the MCU
    """

    def __init__(self, port: str):
        if port not in ServoControlRegisters.__members__:
            raise Exception("Invalid port. Servo motors must be connected to ports S1-S4")

        self.registers = ServoControlRegisters[port].value
        self.__mcu_device = PlateInterface().get_device_mcu()

        self.__lower_duty_cycle = 0
        self.__upper_duty_cycle = 0

        self.set_pwm_frequency(ServoHardwareSpecs.PWM_FREQUENCY)
        self.set_min_pulse_width(ServoHardwareSpecs.MIN_PULSE_WIDTH_MICRO_S)
        self.set_max_pulse_width(ServoHardwareSpecs.MAX_PULSE_WIDTH_MICRO_S)

    def cleanup(self, state=None):
        self.set_target_angle(
            state.angle if state is not None else 0,
            state.speed if state is not None else 0
        )

    @type_check
    def set_min_pulse_width(self, min_width_us: int) -> None:
        self.__mcu_device.write_word(ServoMotorSetup.REGISTER_MIN_PULSE_WIDTH,
                                     min_width_us,
                                     signed=False,
                                     little_endian=True)

        self.__lower_duty_cycle = ServoHardwareSpecs.DUTY_REGISTER_RANGE * ((min_width_us * 1e-6) * self.pwm_frequency())
        self.__lower_duty_cycle = int(round(self.__lower_duty_cycle))

    @type_check
    def set_max_pulse_width(self, max_width_us: int) -> None:
        self.__mcu_device.write_word(ServoMotorSetup.REGISTER_MAX_PULSE_WIDTH,
                                     max_width_us,
                                     signed=False,
                                     little_endian=True)

        self.__upper_duty_cycle = ServoHardwareSpecs.DUTY_REGISTER_RANGE * ((max_width_us * 1e-6) * self.pwm_frequency())
        self.__upper_duty_cycle = int(round(self.__upper_duty_cycle))

    @type_check
    def set_pwm_frequency(self, frequency: int) -> None:
        self.__mcu_device.write_byte(ServoMotorSetup.REGISTER_PWM_FREQUENCY, frequency)

    def pwm_frequency(self) -> int:
        return self.__mcu_device.read_unsigned_byte(ServoMotorSetup.REGISTER_PWM_FREQUENCY)

    def get_current_angle_and_speed(self):
        duty_cycle_and_speed = self.__mcu_device.read_n_signed_bytes(
            self.registers[ServoRegisterTypes.ANGLE_AND_SPEED], number_of_bytes=4, little_endian=True)

        angle_speed_bytes = split_into_bytes(duty_cycle_and_speed, no_of_bytes=4, little_endian=True, signed=True)

        duty_cycle = int.from_bytes(angle_speed_bytes[0:2], byteorder="little", signed=True)

        angle = int(round(interp(duty_cycle,
                                 [self.__lower_duty_cycle, self.__upper_duty_cycle],
                                 [-ServoHardwareSpecs.ANGLE_RANGE / 2, ServoHardwareSpecs.ANGLE_RANGE / 2])))

        speed = int.from_bytes(angle_speed_bytes[2:4], byteorder="little", signed=True) / 10.0

        return angle, speed

    @type_check
    def set_target_angle(self, angle: Union[int, float], speed: Union[int, float] = 50.0):
        mapped_duty_cycle = interp(angle,
                                   [-ServoHardwareSpecs.ANGLE_RANGE / 2, ServoHardwareSpecs.ANGLE_RANGE / 2],
                                   [self.__lower_duty_cycle, self.__upper_duty_cycle])
        mapped_duty_cycle = int(round(mapped_duty_cycle))

        mapped_speed = int(round(speed * 10))

        list_to_send = split_into_bytes(mapped_duty_cycle, 2, signed=True, little_endian=True)
        list_to_send += split_into_bytes(mapped_speed, 2, signed=True, little_endian=True)

        self.__mcu_device.write_n_bytes(self.registers[ServoRegisterTypes.ANGLE_AND_SPEED], list_to_send)

    @type_check
    def set_acceleration_mode(self, mode: int):
        self.__mcu_device.write_byte(self.registers[ServoRegisterTypes.ACC_MODE], mode)
