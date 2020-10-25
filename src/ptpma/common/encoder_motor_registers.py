from enum import Enum


class MotorRegisterTypes:
    CONTROL_MODE = 0
    MODE_0_POWER = 1
    MODE_1_RPM = 2
    MODE_2_RPM_WITH_ROTATIONS = 3
    BRAKE_TYPE = 4
    TACHOMETER = 5
    ODOMETER = 6


EncoderMotorM1 = {
    MotorRegisterTypes.CONTROL_MODE: 0x60,
    MotorRegisterTypes.MODE_0_POWER: 0x64,
    MotorRegisterTypes.MODE_1_RPM: 0x68,
    MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS: 0x6C,
    MotorRegisterTypes.BRAKE_TYPE: 0x70,
    MotorRegisterTypes.TACHOMETER: 0x75,
    MotorRegisterTypes.ODOMETER: 0x7A
}


EncoderMotorM2 = {
    MotorRegisterTypes.CONTROL_MODE: 0x61,
    MotorRegisterTypes.MODE_0_POWER: 0x65,
    MotorRegisterTypes.MODE_1_RPM: 0x69,
    MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS: 0x6D,
    MotorRegisterTypes.BRAKE_TYPE: 0x71,
    MotorRegisterTypes.TACHOMETER: 0x76,
    MotorRegisterTypes.ODOMETER: 0x7B
}


EncoderMotorM3 = {
    MotorRegisterTypes.CONTROL_MODE: 0x62,
    MotorRegisterTypes.MODE_0_POWER: 0x66,
    MotorRegisterTypes.MODE_1_RPM: 0x6A,
    MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS: 0x6E,
    MotorRegisterTypes.BRAKE_TYPE: 0x72,
    MotorRegisterTypes.TACHOMETER: 0x77,
    MotorRegisterTypes.ODOMETER: 0x7C
}


EncoderMotorM4 = {
    MotorRegisterTypes.CONTROL_MODE: 0x63,
    MotorRegisterTypes.MODE_0_POWER: 0x67,
    MotorRegisterTypes.MODE_1_RPM: 0x6B,
    MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS: 0x6F,
    MotorRegisterTypes.BRAKE_TYPE: 0x73,
    MotorRegisterTypes.TACHOMETER: 0x78,
    MotorRegisterTypes.ODOMETER: 0x7D
}


class MotorControlRegisters(Enum):
    M1 = EncoderMotorM1
    M2 = EncoderMotorM2
    M3 = EncoderMotorM3
    M4 = EncoderMotorM4


class MotorControlModes(Enum):
    MODE_0 = 0
    MODE_1 = 1
    MODE_2 = 2
