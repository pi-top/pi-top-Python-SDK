#!/usr/bin/env python3

from .common.imu_registers import ImuDataRegisters, ImuEnableRegisters, ImuRegisterTypes, RawDataRegisterTypes, OrientationDataRegisterTypes, ImuRegisters
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

    def set_imu_config(self, function: ImuRegisterTypes, enable: bool):
        self._mcu_device.write_word(self._enable_registers[function], int(enable), little_endian=True, signed=False)

    def set_acc_config(self, enable: bool):
        self.set_imu_config(ImuRegisterTypes.ACC, enable)
        self._acc_enable = enable

    def set_gyro_config(self, enable: bool):
        self.set_imu_config(ImuRegisterTypes.GYRO, enable)
        self._gyro_enable = enable

    def set_mag_config(self, enable: bool):
        self.set_imu_config(ImuRegisterTypes.MAG, enable)
        self._mag_enable = enable

    def set_orientation_config(self, enable: bool):
        self.set_imu_config(ImuRegisterTypes.ORIENTATION, enable)
        self._orientation_enable = enable

    def read_imu_data(self, data_register: int):
        return self._mcu_device.read_signed_word(data_register, little_endian=True)

    def get_raw_data(self, data_type: int):
        data = {
            'x': self.read_imu_data(ImuDataRegisters[data_type][RawDataRegisterTypes.X]),
            'y': self.read_imu_data(ImuDataRegisters[data_type][RawDataRegisterTypes.Y]),
            'z': self.read_imu_data(ImuDataRegisters[data_type][RawDataRegisterTypes.Z]),
        }

        return data

    def get_orientation_data(self):
        data = {
            'roll': self.read_imu_data(ImuDataRegisters[ImuRegisterTypes.ORIENTATION][OrientationDataRegisterTypes.ROLL]),
            'pitch': self.read_imu_data(ImuDataRegisters[ImuRegisterTypes.ORIENTATION][OrientationDataRegisterTypes.PITCH]),
            'yaw': self.read_imu_data(ImuDataRegisters[ImuRegisterTypes.ORIENTATION][OrientationDataRegisterTypes.YAW])
        }
        return data

    def get_accelerometer_raw(self):
        if not self._acc_enable:
            self.set_acc_config(enable=True)

        return self.get_raw_data(ImuRegisterTypes.ACC)

    def get_gyroscope_raw(self):
        if not self._gyro_enable:
            self.set_gyro_config(enable=True)

        return self.get_raw_data(ImuRegisterTypes.GYRO)

    def get_magnetometer_raw(self):
        if not self._mag_enable:
            self.set_mag_config(enable=True)

        return self.get_raw_data(ImuRegisterTypes.MAG)

