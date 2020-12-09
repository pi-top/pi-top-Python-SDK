#!/usr/bin/env python3

from .common.imu_registers import ImuRegisters, RegisterTypes, RawRegisterTypes, OrientationRegisterTypes, ScaleMappings
from .plate_interface import PlateInterface
import math

g = 9.807

class ImuController:
    """
    Class used to read/write IMU registers from the Expansion Plate MCU
    """
    _ORIENTATION_DATA_SCALE = 100.0
    _MAG_SIGNED_RANGE = 4900.0
    _16BIT_SIGNED_RANGE = 2**15

    def __init__(self):
        self._data_registers = ImuRegisters.DATA
        self._enable_registers = ImuRegisters.ENABLE
        self._config_registers = ImuRegisters.CONFIG
        self._mcu_device = PlateInterface.instance().get_device_mcu()
        self._acc_enable = False
        self._gyro_enable = False
        self._mag_enable = False
        self._orientation_enable = False
        self.acc_scaler = 2
        self.gyro_scaler = 250

    def cleanup(self):
        for name, member in RegisterTypes.__members__.items():
            self._set_imu_config(member.value, enable=False)

    def _set_imu_config(self, imu_function: int, enable: bool):
        self._mcu_device.write_word(self._enable_registers[imu_function], int(enable), little_endian=True, signed=False)

    @property
    def acc_enable(self):
        return self._acc_enable

    @acc_enable.setter
    def acc_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.ACC.value, enable)
        self._acc_enable = enable

    @property
    def gyro_enable(self):
        return self._gyro_enable

    @gyro_enable.setter
    def gyro_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.GYRO.value, enable)
        self._gyro_enable = enable

    @property
    def mag_enable(self):
        return self._mag_enable

    @mag_enable.setter
    def mag_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.MAG.value, enable)
        self._mag_enable = enable

    @property
    def orientation_enable(self):
        return self._mag_enable

    @orientation_enable.setter
    def orientation_enable(self, enable: bool):
        self._set_imu_config(RegisterTypes.ORIENTATION.value, enable)
        self._orientation_enable = enable

    def _data_scale_config_write(self, register_type: int, scaler: int):
        if scaler not in ScaleMappings[register_type].keys():
            raise ValueError("Valid values for scalers are: {}".format(list(ScaleMappings[register_type].keys())))
        byte = ScaleMappings[register_type][scaler]
        self._mcu_device.write_byte(self._config_registers[register_type], byte)

    def _data_scale_config_read(self, register_type: int):
        byte = self._mcu_device.read_unsigned_byte(self._config_registers[register_type])
        scaler = next(key for key, value in ScaleMappings[register_type].items() if value == byte)
        return scaler

    @property
    def acc_scaler(self):
        return self._data_scale_config_read(RegisterTypes.ACC.value)

    @acc_scaler.setter
    def acc_scaler(self, scaler: int):
        self._data_scale_config_write(RegisterTypes.ACC.value, scaler)
        if self.acc_scaler == scaler:
            self._acc_scaler = scaler
        else:
            # if values don't match, repeat trying until they do
            self.acc_scaler = scaler

    @property
    def gyro_scaler(self):
        return self._data_scale_config_read(RegisterTypes.GYRO.value)

    @gyro_scaler.setter
    def gyro_scaler(self, scaler: int):
        self._data_scale_config_write(RegisterTypes.GYRO.value, scaler)
        if self.gyro_scaler == scaler:
            self._gyro_scaler = scaler
        else:
            # if values don't match, repeat trying until they do
            self.gyro_scaler = scaler

    @property
    def accelerometer_raw(self):
        if not self.acc_enable:
            self.acc_enable = True

        imu_acc_raw = self._get_raw_data(RegisterTypes.ACC.value)

        imu_acc_scaled = tuple([axis * g / (self._16BIT_SIGNED_RANGE / float(self._acc_scaler)) for axis in imu_acc_raw])

        return imu_acc_scaled

    @property
    def gyroscope_raw(self):
        if not self.gyro_enable:
            self.gyro_enable = True

        imu_gyro_raw = self._get_raw_data(RegisterTypes.GYRO.value)

        imu_gyro_scaled = tuple([axis / (self._16BIT_SIGNED_RANGE / float(self._gyro_scaler)) for axis in imu_gyro_raw])

        return imu_gyro_scaled

    @property
    def magnetometer_raw(self):
        if not self.mag_enable:
            self.mag_enable = True

        mag_raw = self._get_raw_data(RegisterTypes.MAG.value)

        mag_raw_scaled = tuple(axis * self._MAG_SIGNED_RANGE / self._16BIT_SIGNED_RANGE for axis in mag_raw)

        return mag_raw_scaled

    @property
    def orientation_data(self):
        if not self.orientation_enable:
            self.orientation_enable = True

        roll = self._read_imu_data(
            self._data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.ROLL]) / self._ORIENTATION_DATA_SCALE
        pitch = self._read_imu_data(
            self._data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.PITCH]) / self._ORIENTATION_DATA_SCALE
        yaw = self._read_imu_data(
            self._data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.YAW]) / self._ORIENTATION_DATA_SCALE

        return roll, pitch, yaw

    def _read_imu_data(self, data_register: int):
        return self._mcu_device.read_signed_word(data_register, little_endian=True)

    def _get_raw_data(self, data_type: int):
        x = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.X])
        y = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.Y])
        z = self._read_imu_data(self._data_registers[data_type][RawRegisterTypes.Z])

        return x, y, z
