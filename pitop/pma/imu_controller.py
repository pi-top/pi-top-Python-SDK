#!/usr/bin/env python3

from .common.imu_registers import ImuRegisters, RegisterTypes, RawRegisterTypes, OrientationRegisterTypes
from .plate_interface import PlateInterface


class ImuController:
    """
    Class used to read/write IMU registers from the Expansion Plate MCU
    """
    _MCU_DATA_SCALE = 100.0
    def __init__(self):
        self._data_registers = ImuRegisters.DATA
        self._enable_registers = ImuRegisters.ENABLE
        self._mcu_device = PlateInterface.instance().get_device_mcu()
        self._acc_enable = False
        self._gyro_enable = False
        self._mag_enable = False
        self._orientation_enable = False

    def cleanup(self):
        for name, member in RegisterTypes.__members__.items():
            self._set_imu_config(member.value, enable=False)

    def _set_imu_config(self, imu_function: int, enable: bool):
        self._mcu_device.write_word(self._enable_registers[imu_function], int(enable), little_endian=True, signed=False)

    @property
    def _acc_enable(self):
        return self._acc_enable

    @_acc_enable.setter
    def _acc_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.ACC.value, enable)
        self._acc_enable = enable

    @property
    def _gyro_enable(self):
        return self._gyro_enable

    @_gyro_enable.setter
    def _gyro_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.GYRO.value, enable)
        self._gyro_enable = enable

    @property
    def _mag_enable(self):
        return self._mag_enable

    @_mag_enable.setter
    def _mag_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.MAG.value, enable)
        self._mag_enable = enable

    @property
    def _orientation_enable(self):
        return self._mag_enable

    @_orientation_enable.setter
    def _orientation_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.ORIENTATION.value, enable)
        self._orientation_enable = enable

    @property
    def accelerometer_raw(self):
        if not self._orientation_enable:
            self._acc_enable = True

        return self._get_raw_data(RegisterTypes.ACC.value)

    @property
    def gyroscope_raw(self):
        if not self._gyro_enable:
            self._gyro_enable = True

        return self._get_raw_data(RegisterTypes.GYRO.value)

    @property
    def magnetometer_raw(self):
        if not self._mag_enable:
            self._mag_enable = True

        return self._get_raw_data(RegisterTypes.MAG.value)

    @property
    def orientation_data(self):

        roll = self._read_imu_data(
            self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.ROLL]) / self._MCU_DATA_SCALE,

        pitch = self._read_imu_data(
                self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.PITCH]) / self._MCU_DATA_SCALE,

        yaw = self._read_imu_data(
                self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.YAW]) / self._MCU_DATA_SCALE

        return roll, pitch, yaw

    def _read_imu_data(self, data_register: int):
        return self._mcu_device.read_signed_word(data_register, little_endian=True)

    def _get_raw_data(self, data_type: int):
        x = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.X]) / self._MCU_DATA_SCALE
        y = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.Y]) / self._MCU_DATA_SCALE
        z = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.Z]) / self._MCU_DATA_SCALE

        return x, y, z
