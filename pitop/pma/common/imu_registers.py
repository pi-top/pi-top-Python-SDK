class RegisterTypes:
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


class MagCalRegisterTypes:
    HARD = 0
    SOFT = 1


class MagCalHardTypes:
    X = 0
    Y = 1
    Z = 2


class MagCalSoftTypes:
    XX = 0
    YY = 1
    ZZ = 2
    XY = 3
    XZ = 4
    YZ = 5


ImuEnableRegisters = {
    RegisterTypes.ACC: 0x90,
    RegisterTypes.GYRO: 0x91,
    RegisterTypes.MAG: 0x92,
    RegisterTypes.ORIENTATION: 0x93
}

ImuConfigRegisters = {
    RegisterTypes.ACC: 0xA0,
    RegisterTypes.GYRO: 0xA2
}

MagCalibrationRegisters = {
    MagCalRegisterTypes.HARD: {
        MagCalHardTypes.X: 0xB0,
        MagCalHardTypes.Y: 0xB1,
        MagCalHardTypes.Z: 0xB2,
    },
    MagCalRegisterTypes.SOFT: {
        MagCalSoftTypes.XX: 0xB3,
        MagCalSoftTypes.YY: 0xB4,
        MagCalSoftTypes.ZZ: 0xB5,
        MagCalSoftTypes.XY: 0xB6,
        MagCalSoftTypes.XZ: 0xB7,
        MagCalSoftTypes.YZ: 0xB8,

    }
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
    RegisterTypes.ACC: {
        RawRegisterTypes.X: 0x80,
        RawRegisterTypes.Y: 0x81,
        RawRegisterTypes.Z: 0x82
    },
    RegisterTypes.GYRO: {
        RawRegisterTypes.X: 0x83,
        RawRegisterTypes.Y: 0x84,
        RawRegisterTypes.Z: 0x85
    },
    RegisterTypes.MAG: {
        RawRegisterTypes.X: 0x86,
        RawRegisterTypes.Y: 0x87,
        RawRegisterTypes.Z: 0x88
    },
    RegisterTypes.ORIENTATION: {
        OrientationRegisterTypes.ROLL: 0x89,
        OrientationRegisterTypes.PITCH: 0x8A,
        OrientationRegisterTypes.YAW: 0x8B
    }
}


class ImuRegisters:
    ENABLE = ImuEnableRegisters
    DATA = ImuDataRegisters
    CONFIG = ImuConfigRegisters
    MAGCAL = MagCalibrationRegisters
