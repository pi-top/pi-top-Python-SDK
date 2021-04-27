import math


def normalize_angle(angle):
    """Converts to range -pi to +pi to prevent unstable behaviour when going
    from 0 to 2*pi with slight turn.

    :param angle: angle in radians
    :return: angle in radians normalized to range -pi to +pi
    """
    return (angle + math.pi) % (2 * math.pi) - math.pi
