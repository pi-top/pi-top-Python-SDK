from dataclasses import dataclass


@dataclass
class Twist:

    @dataclass
    class linear:
        x: float
        y: float
        z: float

    @dataclass
    class angular:
        x: float
        y: float
        z: float
