#!/usr/bin/env python3

from .common.imu_registers import ImuRegisters, RegisterTypes, RawRegisterTypes, OrientationRegisterTypes, ScaleMappings
from .common.imu_registers import MagCalHardTypes, MagCalSoftTypes, MagCalRegisterTypes
from .plate_interface import PlateInterface
from pitopcommon.logger import PTLogger
import numpy as np


class ImuController:
    """
    Class used to read/write IMU registers from the Expansion Plate MCU
    """
    __ORIENTATION_DATA_SCALE = 100.0
    __MAG_SIGNED_RANGE = 4900.0
    __16BIT_SIGNED_RANGE = 2 ** 15
    __HARD_IRON_SCALE_FACTOR = 10.0
    __SOFT_IRON_SCALE_FACTOR = 1000.0

    def __init__(self):
        # TODO - review member variables vs get/set properties
        self.acc_scaler = 2
        self.gyro_scaler = 250

        self.__data_registers = ImuRegisters.DATA
        self.__enable_registers = ImuRegisters.ENABLE
        self.__config_registers = ImuRegisters.CONFIG
        self.__mag_cal_registers = ImuRegisters.MAGCAL
        self.__mcu_device = PlateInterface().get_device_mcu()
        self.__acc_enable = False
        self.__gyro_enable = False
        self.__mag_enable = False
        self.__orientation_enable = False
        self.__acc_scaler = None
        self.__gyro_scaler = None
        self.__mag_cal_error_count = 0

    def cleanup(self):
        self.acc_enable = False
        self.gyro_enable = False
        self.mag_enable = False
        self.orientation_enable = False

    def __set_imu_config(self, imu_function: int, enable: bool):
        self.__mcu_device.write_word(self.__enable_registers[imu_function], int(enable), little_endian=True, signed=False)

    @property
    def acc_enable(self):
        return self.__acc_enable

    @acc_enable.setter
    def acc_enable(self, enable: bool):
        self.__set_imu_config(RegisterTypes.ACC, enable)
        self.__acc_enable = enable

    @property
    def gyro_enable(self):
        return self.__gyro_enable

    @gyro_enable.setter
    def gyro_enable(self, enable: bool):
        self.__set_imu_config(RegisterTypes.GYRO, enable)
        self.__gyro_enable = enable

    @property
    def mag_enable(self):
        return self.__mag_enable

    @mag_enable.setter
    def mag_enable(self, enable: bool):
        self.__set_imu_config(RegisterTypes.MAG, enable)
        self.__mag_enable = enable

    @property
    def orientation_enable(self):
        return self.__orientation_enable

    @orientation_enable.setter
    def orientation_enable(self, enable: bool):
        self.__set_imu_config(RegisterTypes.ORIENTATION, enable)
        self.__orientation_enable = enable

    def __data_scale_config_write(self, register_type: int, scaler: int):
        if scaler not in ScaleMappings[register_type].keys():
            raise ValueError(f"Valid values for scalers are: {list(ScaleMappings[register_type].keys())}")
        byte = ScaleMappings[register_type][scaler]
        self.__mcu_device.write_byte(self.__config_registers[register_type], byte)

    def __data_scale_config_read(self, register_type: int):
        byte = self.__mcu_device.read_unsigned_byte(self.__config_registers[register_type])
        scaler = next(key for key, value in ScaleMappings[register_type].items() if value == byte)
        return scaler

    @property
    def acc_scaler(self):
        return self.__data_scale_config_read(RegisterTypes.ACC)

    @acc_scaler.setter
    def acc_scaler(self, scaler: int):
        self.__data_scale_config_write(RegisterTypes.ACC, scaler)
        if self.acc_scaler == scaler:
            self.__acc_scaler = scaler
        else:
            # if values don't match, repeat trying until they do
            self.acc_scaler = scaler

    @property
    def gyro_scaler(self):
        return self.__data_scale_config_read(RegisterTypes.GYRO)

    @gyro_scaler.setter
    def gyro_scaler(self, scaler: int):
        self.__data_scale_config_write(RegisterTypes.GYRO, scaler)
        if self.gyro_scaler == scaler:
            self.__gyro_scaler = scaler
        else:
            # if values don't match, repeat trying until they do
            self.gyro_scaler = scaler

    @property
    def accelerometer_raw(self):
        if not self.acc_enable:
            self.acc_enable = True

        imu_acc_raw = self.__get_raw_data(RegisterTypes.ACC)

        imu_acc_scaled = tuple([axis / (self.__16BIT_SIGNED_RANGE / float(self.__acc_scaler)) for axis in imu_acc_raw])

        return imu_acc_scaled

    @property
    def gyroscope_raw(self):
        if not self.gyro_enable:
            self.gyro_enable = True

        imu_gyro_raw = self.__get_raw_data(RegisterTypes.GYRO)

        imu_gyro_scaled = tuple([axis / (self.__16BIT_SIGNED_RANGE / float(self.__gyro_scaler)) for axis in imu_gyro_raw])

        return imu_gyro_scaled

    @property
    def magnetometer_raw(self):
        if not self.mag_enable:
            self.mag_enable = True

        mag_raw = self.__get_raw_data(RegisterTypes.MAG)

        mag_raw_scaled = tuple(axis * self.__MAG_SIGNED_RANGE / self.__16BIT_SIGNED_RANGE for axis in mag_raw)

        return mag_raw_scaled

    @property
    def orientation_data(self):
        if not self.orientation_enable:
            self.orientation_enable = True

        roll = self.__read_imu_data(
            self.__data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.ROLL]) / self.__ORIENTATION_DATA_SCALE
        pitch = self.__read_imu_data(
            self.__data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.PITCH]) / self.__ORIENTATION_DATA_SCALE
        yaw = self.__read_imu_data(
            self.__data_registers[
                RegisterTypes.ORIENTATION][OrientationRegisterTypes.YAW]) / self.__ORIENTATION_DATA_SCALE

        return roll, pitch, yaw

    def read_mag_cal_params(self):
        x, y, z = self.__read_mag_cal_hard()
        hard_iron_offset = np.array([[x, y, z]]).T / self.__HARD_IRON_SCALE_FACTOR
        xx, yy, zz, xy, xz, yz = self.__read_mag_cal_soft()
        soft_iron_matrix = np.array([[xx, xy, xz],
                                     [xy, yy, yz],
                                     [xz, yz, zz]]) / self.__SOFT_IRON_SCALE_FACTOR
        return hard_iron_offset, soft_iron_matrix

    def write_mag_cal_params(self, hard_iron_offset, soft_iron_matrix):
        hard_x = int(round(hard_iron_offset[0][0]))
        hard_y = int(round(hard_iron_offset[1][0]))
        hard_z = int(round(hard_iron_offset[2][0]))

        self.__write_mag_cal(hard_x, MagCalRegisterTypes.HARD, MagCalHardTypes.X)
        self.__write_mag_cal(hard_y, MagCalRegisterTypes.HARD, MagCalHardTypes.Y)
        self.__write_mag_cal(hard_z, MagCalRegisterTypes.HARD, MagCalHardTypes.Z)

        # matrix is symmetric so only need 6 values
        soft_xx = int(round(soft_iron_matrix[0][0] * self.__SOFT_IRON_SCALE_FACTOR))
        soft_xy = int(round(soft_iron_matrix[0][1] * self.__SOFT_IRON_SCALE_FACTOR))
        soft_xz = int(round(soft_iron_matrix[0][2] * self.__SOFT_IRON_SCALE_FACTOR))
        soft_yy = int(round(soft_iron_matrix[1][1] * self.__SOFT_IRON_SCALE_FACTOR))
        soft_yz = int(round(soft_iron_matrix[1][2] * self.__SOFT_IRON_SCALE_FACTOR))
        soft_zz = int(round(soft_iron_matrix[2][2] * self.__SOFT_IRON_SCALE_FACTOR))

        self.__write_mag_cal(soft_xx, MagCalRegisterTypes.SOFT, MagCalSoftTypes.XX)
        self.__write_mag_cal(soft_yy, MagCalRegisterTypes.SOFT, MagCalSoftTypes.YY)
        self.__write_mag_cal(soft_zz, MagCalRegisterTypes.SOFT, MagCalSoftTypes.ZZ)
        self.__write_mag_cal(soft_xy, MagCalRegisterTypes.SOFT, MagCalSoftTypes.XY)
        self.__write_mag_cal(soft_xz, MagCalRegisterTypes.SOFT, MagCalSoftTypes.XZ)
        self.__write_mag_cal(soft_yz, MagCalRegisterTypes.SOFT, MagCalSoftTypes.YZ)

        # check that the writes were successful
        hard_iron_offset_read, soft_iron_matrix_read = self.read_mag_cal_params()
        equal_hard = np.allclose(hard_iron_offset_read, hard_iron_offset, atol=1 / self.__HARD_IRON_SCALE_FACTOR)
        equal_soft = np.allclose(soft_iron_matrix_read, soft_iron_matrix, atol=1 / self.__SOFT_IRON_SCALE_FACTOR)
        if not equal_hard or not equal_soft:
            self.__mag_cal_error_count += 1
            if self.__mag_cal_error_count > 5:
                PTLogger.error("Cannot write magnetometer calibration settings, try re-docking the pi-top [4] to "
                               "Expansion Plate")
                exit()
            # if values don't match, repeat trying until they do
            self.write_mag_cal_params(hard_iron_offset, soft_iron_matrix)
        else:
            self.__mag_cal_error_count = 0

    def __read_imu_data(self, data_register: int):
        return self.__mcu_device.read_signed_word(data_register, little_endian=True)

    def __get_raw_data(self, data_type: int):
        x = self.__read_imu_data(self.__data_registers[data_type][RawRegisterTypes.X])
        y = self.__read_imu_data(self.__data_registers[data_type][RawRegisterTypes.Y])
        z = self.__read_imu_data(self.__data_registers[data_type][RawRegisterTypes.Z])

        return x, y, z

    def __write_mag_cal(self, word, register_type, calibration_type):
        self.__mcu_device.write_word(self.__mag_cal_registers[register_type][calibration_type], word, little_endian=True,
                                     signed=True)

    def __read_mag_cal_hard(self):
        data = []
        for register_key, register_value in self.__mag_cal_registers[MagCalRegisterTypes.HARD].items():
            data.append(self.__mcu_device.read_signed_word(register_value, little_endian=True))
        x, y, z = data
        return x, y, z

    def __read_mag_cal_soft(self):
        data = []
        for register_key, register_value in self.__mag_cal_registers[MagCalRegisterTypes.SOFT].items():
            data.append(self.__mcu_device.read_signed_word(register_value, little_endian=True))
        xx, yy, zz, xy, xz, yz = data
        return xx, yy, zz, xy, xz, yz
