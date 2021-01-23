from dataclasses import dataclass


@dataclass
class Twist:
    # TODO: check if this is common practice to have sub-dataclasses
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
