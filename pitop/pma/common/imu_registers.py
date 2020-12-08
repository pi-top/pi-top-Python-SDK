from enum import Enum


class RegisterTypes(Enum):
    ACC = 0
    GYRO = 1
    MAG = 2
    ORIENTATION = 3


class RawRegisterTypes:
    X = 0
    Y = 1
    Z = 2


class OrientationRegisterTypes:
    ROLL = 0
    PITCH = 1
    YAW = 2


ImuEnableRegisters = {
    RegisterTypes.ACC.value: 0x90,
    RegisterTypes.GYRO.value: 0x91,
    RegisterTypes.MAG.value: 0x92,
    RegisterTypes.ORIENTATION.value: 0x93
}

ImuConfigRegisters = {
    RegisterTypes.ACC.value: 0xA0,
    RegisterTypes.GYRO.value: 0xA2
}

ScaleMappings = {
    RegisterTypes.ACC: {
        2: 0x00,
        4: 0x01,
        8: 0x02,
        16: 0x03
    },
    RegisterTypes.GYRO: {
        250: 0x00,
        500: 0x01,
        1000: 0x02,
        2000: 0x03
    }
}

ImuDataRegisters = {
    RegisterTypes.ACC.value: {
        RawRegisterTypes.X: 0x80,
        RawRegisterTypes.Y: 0x81,
        RawRegisterTypes.Z: 0x82
    },
    RegisterTypes.GYRO.value: {
        RawRegisterTypes.X: 0x83,
        RawRegisterTypes.Y: 0x84,
        RawRegisterTypes.Z: 0x85
    },
    RegisterTypes.MAG.value: {
        RawRegisterTypes.X: 0x86,
        RawRegisterTypes.Y: 0x87,
        RawRegisterTypes.Z: 0x88
    },
    RegisterTypes.ORIENTATION.value: {
        OrientationRegisterTypes.ROLL: 0x89,
        OrientationRegisterTypes.PITCH: 0x8A,
        OrientationRegisterTypes.YAW: 0x8B
    }
}


class ImuRegisters:
    ENABLE = ImuEnableRegisters
    DATA = ImuDataRegisters
    CONFIG = ImuConfigRegisters
