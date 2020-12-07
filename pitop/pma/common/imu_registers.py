from dataclasses import dataclass


@dataclass
class ImuDataRegisters:
    @dataclass
    class acceleration:
        x: int = 0x80
        y: int = 0x81
        z: int = 0x82

    @dataclass
    class gyroscope:
        x: int = 0x83
        y: int = 0x84
        z: int = 0x85

    @dataclass
    class magnetometer:
        x: int = 0x86
        y: int = 0x87
        z: int = 0x88

    @dataclass
    class orientation:
        pitch: int = 0x89
        roll: int = 0x8A
        yaw: int = 0x8B


class ImuEnableRegisterTypes:
    ACC = 0
    GYRO = 1
    MAG = 2
    ORIENTATION = 3


ImuEnableRegisters = {
    ImuEnableRegisterTypes.ACC: 0x90,
    ImuEnableRegisterTypes.GYRO: 0x91,
    ImuEnableRegisterTypes.MAG: 0x92,
    ImuEnableRegisterTypes.ORIENTATION: 0x93
}



