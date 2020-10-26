from enum import IntEnum


class BrakingType(IntEnum):
    """
    Braking types
    """
    COAST = 0
    BRAKE = 1


class ForwardDirection(IntEnum):
    """
    Forward directions
    """
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


class Direction(IntEnum):
    """
    Directions
    """
    FORWARD = 1
    BACK = -1
