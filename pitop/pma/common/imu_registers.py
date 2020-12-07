from dataclasses import dataclass

@dataclass
class ImuRegisters:

    @dataclass
    class Acceleration:
        x: int = 0x80
        y: int = 0x81
        z: int = 0x82

    @dataclass
    class Gyroscope:
        x: int = 0x83
        y: int = 0x84
        z: int = 0x85

    @dataclass
    class Magnetometer:
        x: int = 0x86
        y: int = 0x87
        z: int = 0x88

    @dataclass
    class Orientation:
        pitch: int = 0x89
        roll: int = 0x8A
        yaw: int = 0x8B
