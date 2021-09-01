class UltrasonicRegisterTypes:
    CONFIG = 0
    DATA = 1


UltrasonicA1 = {
    UltrasonicRegisterTypes.CONFIG: 0x0C,
    UltrasonicRegisterTypes.DATA: 0x0E,
}


UltrasonicA3 = {
    UltrasonicRegisterTypes.CONFIG: 0x0D,
    UltrasonicRegisterTypes.DATA: 0x0F,
}

UltrasonicRegisters = {
    "A1": UltrasonicA1,
    "A3": UltrasonicA3,
}

UltrasonicConfigSettings = {
    "A1": 0xA1,
    "A3": 0xA3,
}
