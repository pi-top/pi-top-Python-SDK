from dataclasses import dataclass
from enum import Enum


class ImuRegisterTypes:
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
    ImuRegisterTypes.ACC: 0x90,
    ImuRegisterTypes.GYRO: 0x91,
    ImuRegisterTypes.MAG: 0x92,
    ImuRegisterTypes.ORIENTATION: 0x93
}

ImuDataRegisters = {
    ImuRegisterTypes.ACC: {
        RawDataRegisterTypes.X: 0x80,
        RawDataRegisterTypes.Y: 0x81,
        RawDataRegisterTypes.Z: 0x82
    },
    ImuRegisterTypes.GYRO: {
        RawDataRegisterTypes.X: 0x83,
        RawDataRegisterTypes.Y: 0x84,
        RawDataRegisterTypes.Z: 0x85
    },
    ImuRegisterTypes.MAG: {
        RawDataRegisterTypes.X: 0x86,
        RawDataRegisterTypes.Y: 0x87,
        RawDataRegisterTypes.Z: 0x88
    },
    ImuRegisterTypes.ORIENTATION: {
        OrientationDataRegisterTypes.ROLL: 0x89,
        OrientationDataRegisterTypes.PITCH: 0x8A,
        OrientationDataRegisterTypes.YAW: 0x8B
    }
}
