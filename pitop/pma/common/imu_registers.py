from dataclasses import dataclass
from enum import Enum


class RegisterTypes(Enum):
    ACC = 0
    GYRO = 1
    MAG = 2
    ORIENTATION = 3


class RawDataRegisterTypes:
    X = 0
    Y = 1
    Z = 2


class OrientationDataRegisterTypes:
    ROLL = 0
    PITCH = 1
    YAW = 2


ImuEnableRegisters = {
    RegisterTypes.ACC.value: 0x90,
    RegisterTypes.GYRO.value: 0x91,
    RegisterTypes.MAG.value: 0x92,
    RegisterTypes.ORIENTATION.value: 0x93
}

ImuDataRegisters = {
    RegisterTypes.ACC.value: {
        RawDataRegisterTypes.X: 0x80,
        RawDataRegisterTypes.Y: 0x81,
        RawDataRegisterTypes.Z: 0x82
    },
    RegisterTypes.GYRO.value: {
        RawDataRegisterTypes.X: 0x83,
        RawDataRegisterTypes.Y: 0x84,
        RawDataRegisterTypes.Z: 0x85
    },
    RegisterTypes.MAG.value: {
        RawDataRegisterTypes.X: 0x86,
        RawDataRegisterTypes.Y: 0x87,
        RawDataRegisterTypes.Z: 0x88
    },
    RegisterTypes.ORIENTATION.value: {
        OrientationDataRegisterTypes.ROLL: 0x89,
        OrientationDataRegisterTypes.PITCH: 0x8A,
        OrientationDataRegisterTypes.YAW: 0x8B
    }
}


class ImuRegisters:
    ENABLE = ImuEnableRegisters
    DATA = ImuDataRegisters
