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

    def set_imu_config(self, function: ImuEnableRegisterTypes, enable: bool):
        self._mcu_device.write_word(self._enable_registers[function], int(enable), little_endian=True, signed=False)

    def set_acc_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.ACC, enable)

    def set_gyro_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.GYRO, enable)

    def set_mag_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.MAG, enable)

    def set_orientation_config(self, enable: bool):
        self.set_imu_config(ImuEnableRegisterTypes.ORIENTATION, enable)
