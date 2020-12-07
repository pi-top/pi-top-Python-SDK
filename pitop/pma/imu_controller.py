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
            self.set_imu_config(member.value, enable=False)

    def set_imu_config(self, imu_function: int, enable: bool):
        self._mcu_device.write_word(self._enable_registers[imu_function], int(enable), little_endian=True, signed=False)

    @property
    def acc_enable(self):
        return self._acc_enable

    @acc_enable.setter
    def acc_enable(self, enable: bool):
        self.set_imu_config(RegisterTypes.ACC.value, enable)
        self._acc_enable = enable

    @property
    def gyro_enable(self):
        return self._gyro_enable

    @gyro_enable.setter
    def gyro_enable(self, enable: bool):
        self.set_imu_config(RegisterTypes.GYRO.value, enable)
        self._gyro_enable = enable

    @property
    def mag_enable(self):
        return self._mag_enable

    @mag_enable.setter
    def mag_enable(self, enable: bool):
        self.set_imu_config(RegisterTypes.MAG.value, enable)
        self._mag_enable = enable

    @property
    def orientation_enable(self):
        return self._mag_enable

    @orientation_enable.setter
    def orientation_enable(self, enable: bool):
        self.set_imu_config(RegisterTypes.ORIENTATION.value, enable)
        self._orientation_enable = enable

    def read_imu_data(self, data_register: int):
        return self._mcu_device.read_signed_word(data_register, little_endian=True)

    def get_raw_data(self, data_type: int):
        x = self.read_imu_data(self._data_registers[data_type][RawRegisterTypes.X]) / self._MCU_DATA_SCALE
        y = self.read_imu_data(self._data_registers[data_type][RawRegisterTypes.Y]) / self._MCU_DATA_SCALE
        z = self.read_imu_data(self._data_registers[data_type][RawRegisterTypes.Z]) / self._MCU_DATA_SCALE

        return x, y, z

    def get_orientation_data(self):

        roll = self.read_imu_data(
            self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.ROLL]) / self._MCU_DATA_SCALE,

        pitch = self.read_imu_data(
                self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.PITCH]) / self._MCU_DATA_SCALE,

        yaw = self.read_imu_data(
                self._data_registers[RegisterTypes.ORIENTATION][OrientationRegisterTypes.YAW]) / self._MCU_DATA_SCALE

        return roll, pitch, yaw

    def get_accelerometer_raw(self):
        if not self._acc_enable:
            self.acc_enable = True

        return self.get_raw_data(RegisterTypes.ACC.value)

    def get_gyroscope_raw(self):
        if not self._gyro_enable:
            self.gyro_enable = True

        return self.get_raw_data(RegisterTypes.GYRO.value)

    def get_magnetometer_raw(self):
        if not self._mag_enable:
            self.mag_enable = True

        return self.get_raw_data(RegisterTypes.MAG.value)

