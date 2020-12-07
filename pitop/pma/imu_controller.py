#!/usr/bin/env python3

from .common.imu_registers import ImuDataRegisters, ImuEnableRegisters, ImuEnableRegisterTypes
from .plate_interface import PlateInterface


class ImuController:
    """
    Class used to read/write IMU registers from the Expansion Plate MCU
    """
    def __init__(self):
        self._data_registers = ImuDataRegisters
        self._enable_registers = ImuEnableRegisters
        self._mcu_device = PlateInterface.instance().get_device_mcu()
        self._acc_enable = False
        self._gyro_enable = False
        self._mag_enable = False
        self._orientation_enable = False

    def set_imu_config(self, function: ImuEnableRegisterTypes, enable: bool):
        self._mcu_device.write_word(self._enable_registers[function], int(enable), little_endian=True, signed=False)

    def set_acc_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.ACC, enable)
        self._acc_enable = enable

    def set_gyro_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.GYRO, enable)
        self._gyro_enable = enable

    def set_mag_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.MAG, enable)
        self._mag_enable = enable

    def set_orientation_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.ORIENTATION, enable)
        self._orientation_enable = enable

    def read_imu_data(self, data_type: int):
        return self._mcu_device.read_signed_word(data_type, little_endian=True)

    def get_accelerometer_raw(self):
        if not self._acc_enable:
            self.set_acc_config(enable=True)

        acc_data = {
            'x': self.read_imu_data(ImuDataRegisters.acceleration.x),
            'y': self.read_imu_data(ImuDataRegisters.acceleration.y),
            'z': self.read_imu_data(ImuDataRegisters.acceleration.z),
        }

        return acc_data

    def get_gyroscope_raw(self):
        if not self._gyro_enable:
            self.set_gyro_config(enable=True)

        gyro_data = {
            'x': self.read_imu_data(ImuDataRegisters.gyroscope.x),
            'y': self.read_imu_data(ImuDataRegisters.gyroscope.y),
            'z': self.read_imu_data(ImuDataRegisters.gyroscope.z),
        }

        return gyro_data

    def get_magnetometer_raw(self):
        if not self._mag_enable:
            self.set_mag_config(enable=True)

        mag_data = {
            'x': self.read_imu_data(ImuDataRegisters.magnetometer.x),
            'y': self.read_imu_data(ImuDataRegisters.magnetometer.y),
            'z': self.read_imu_data(ImuDataRegisters.magnetometer.z),
        }

        return mag_data

