#!/usr/bin/env python3

from .common.imu_registers import ImuRegisters
from .plate_interface import PlateInterface

class ImuController:
    """
    Class used to read/write IMU registers from the Expansion Plate MCU
    """
    def __init__(self):
        self._registers = ImuRegisters
        self._mcu_device = PlateInterface.instance().get_device_mcu()
        print(self._registers.Acceleration.x)




