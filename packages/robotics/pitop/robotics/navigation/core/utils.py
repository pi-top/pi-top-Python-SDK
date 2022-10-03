import math


def normalize_angle(angle):
    """Converts to range -pi to +pi to prevent unstable behaviour when going
    from 0 to 2*pi with slight turn.

    :param angle: angle in radians
    :return: angle in radians normalized to range -pi to +pi
    """
    return (angle + math.pi) % (2 * math.pi) - math.pi


def verify_callback(callback):
    if callback is None:
        return None
    if not callable(callback):
        raise ValueError("callback should be a callable function.")

    from inspect import getfullargspec

    arg_spec = getfullargspec(callback)
    number_of_arguments = len(arg_spec.args)
    number_of_default_arguments = (
        len(arg_spec.defaults) if arg_spec.defaults is not None else 0
    )
    if number_of_arguments == 0:
        return callback
    if (
        arg_spec.args[0] in ("self", "_mock_self")
        and (number_of_arguments - number_of_default_arguments) == 1
    ):
        return callback
    if number_of_arguments != number_of_default_arguments:
        raise ValueError("callback should have no non-default keyword arguments.")
    return callback
