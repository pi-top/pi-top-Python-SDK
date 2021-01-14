from typing import Tuple

from pitopcommon.bitwise_ops import split_into_bytes, join_bytes
from .plate_interface import PlateInterface
from .common import type_check
from .common.encoder_motor_registers import (
    MotorRegisterTypes,
    MotorControlRegisters,
    MotorControlModes)


class EncoderMotorController:
    """
    Class used to read/write motor encoder registers from the MCU
    """

    __MAX_DC_MOTOR_RPM = 6000

    def __init__(self, port: str, braking_type: int = 0) -> None:
        if port not in MotorControlRegisters.__members__:
            raise Exception("Invalid port. Motors must be connected to ports M0-M3")

        self.__mcu_device = PlateInterface().get_device_mcu()
        self.registers = MotorControlRegisters[port].value
        self.set_braking_type(braking_type)

    def control_mode(self) -> MotorControlModes:
        reported_control_mode = self.__mcu_device.read_unsigned_byte(self.registers[MotorRegisterTypes.CONTROL_MODE])
        return MotorControlModes(reported_control_mode)

    @type_check
    def set_control_mode(self, mode: MotorControlModes) -> None:
        self.__mcu_device.write_byte(self.registers[MotorRegisterTypes.CONTROL_MODE], mode.value)

    def braking_type(self) -> int:
        return self.__mcu_device.read_unsigned_byte(self.registers[MotorRegisterTypes.BRAKE_TYPE])

    @type_check
    def set_braking_type(self, brake_type: int) -> None:
        if brake_type not in (0, 1):
            raise ValueError("Brake type must be 0 or 1")

        self.__mcu_device.write_byte(self.registers[MotorRegisterTypes.BRAKE_TYPE], brake_type)

    def tachometer(self) -> int:
        tachometer_data = 99999
        while abs(tachometer_data) > self.__MAX_DC_MOTOR_RPM:
            tachometer_data = self.__mcu_device.read_signed_word(self.registers[MotorRegisterTypes.TACHOMETER], little_endian=True)

        return tachometer_data

    def odometer(self) -> int:
        rotation_counter = self.__mcu_device.read_n_signed_bytes(self.registers[MotorRegisterTypes.ODOMETER], 4, little_endian=True)

        return rotation_counter

    @type_check
    def set_odometer(self, rotations: int) -> None:
        list_to_send = split_into_bytes(rotations, 4, signed=True, little_endian=True)
        self.__mcu_device.write_n_bytes(self.registers[MotorRegisterTypes.ODOMETER], list_to_send)

    def stop(self):
        current_control_mode = self.control_mode()

        if current_control_mode == MotorControlModes.MODE_0:
            self.set_power(0)
        elif current_control_mode == MotorControlModes.MODE_1:
            self.set_rpm_control(0)
        elif current_control_mode == MotorControlModes.MODE_2:
            self.set_rpm_with_rotations(0, 0)

    # -------------------------------------------------------------------------------------------------------------------
    # CONTROL MODE 0

    def power(self) -> int:
        if self.control_mode() != MotorControlModes.MODE_0:
            return None

        return self.__mcu_device.read_signed_word(self.registers[MotorRegisterTypes.MODE_0_POWER], little_endian=True)

    @type_check
    def set_power(self, power: int) -> None:
        if power < -1000 or power > 1000:
            raise ValueError("Power value sent to Expansion Plate needs to be from -1000 to +1000")

        self.set_control_mode(MotorControlModes.MODE_0)
        self.__mcu_device.write_word(self.registers[MotorRegisterTypes.MODE_0_POWER], power, little_endian=True, signed=True)

    # -------------------------------------------------------------------------------------------------------------------
    # CONTROL MODE 1

    def rpm_control(self) -> int:
        if self.control_mode() != MotorControlModes.MODE_1:
            return None

        return self.__mcu_device.read_signed_word(self.registers[MotorRegisterTypes.MODE_1_RPM], little_endian=True)

    @type_check
    def set_rpm_control(self, rpm: int) -> None:
        self.set_control_mode(MotorControlModes.MODE_1)
        self.__mcu_device.write_word(self.registers[MotorRegisterTypes.MODE_1_RPM], rpm, signed=True, little_endian=True)

    # -------------------------------------------------------------------------------------------------------------------
    # CONTROL MODE 2

    def rpm_with_rotations(self) -> Tuple[int, int]:
        if self.control_mode() != MotorControlModes.MODE_2:
            return None

        value = self.__mcu_device.read_n_unsigned_bytes(
            self.registers[MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS], 4, little_endian=True)
        value_in_bytes = split_into_bytes(value, 4, little_endian=True)

        speed = join_bytes(value_in_bytes[0:2])
        rotations = join_bytes(value_in_bytes[2:4])

        return speed, rotations

    @type_check
    def set_rpm_with_rotations(self, rpm: int, rotations_to_complete: int) -> None:
        self.set_control_mode(MotorControlModes.MODE_2)
        list_to_send = split_into_bytes(rotations_to_complete, 2, signed=True, little_endian=True) + \
            split_into_bytes(rpm, 2, signed=True, little_endian=True)
        self.__mcu_device.write_n_bytes(self.registers[MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS], list_to_send)
