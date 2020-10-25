from enum import Enum


class ServoRegisterTypes:
    CONTROL_MODE = 0
    SPEED = 1
    ANGLE_AND_SPEED = 2


ServoMotorS1 = {
    ServoRegisterTypes.CONTROL_MODE: 0x50,
    ServoRegisterTypes.SPEED: 0x56,
    ServoRegisterTypes.ANGLE_AND_SPEED: 0x5C
}

ServoMotorS2 = {
    ServoRegisterTypes.CONTROL_MODE: 0x51,
    ServoRegisterTypes.SPEED: 0x57,
    ServoRegisterTypes.ANGLE_AND_SPEED: 0x5D
}

ServoMotorS3 = {
    ServoRegisterTypes.CONTROL_MODE: 0x52,
    ServoRegisterTypes.SPEED: 0x58,
    ServoRegisterTypes.ANGLE_AND_SPEED: 0x5E
}

ServoMotorS4 = {
    ServoRegisterTypes.CONTROL_MODE: 0x53,
    ServoRegisterTypes.SPEED: 0x59,
    ServoRegisterTypes.ANGLE_AND_SPEED: 0x5F
}


class ServoControlRegisters(Enum):
    S1 = ServoMotorS1
    S2 = ServoMotorS2
    S3 = ServoMotorS3
    S4 = ServoMotorS4


class ServoMotorSetup:
    REGISTER_MIN_PULSE_WIDTH = 0x4A
    REGISTER_MAX_PULSE_WIDTH = 0x4B
    REGISTER_PWM_FREQUENCY = 0x4C


class ServoControlModes(Enum):
    MODE_0 = 0
    MODE_1 = 1
