from typing import get_type_hints
from functools import wraps
from inspect import getfullargspec


# Each port has two gpio pins associated with it
# Default pin for each class is "1"
# Convert Port for use with standard BCM pins
Port = {
    "A0": {"1": 0, "2": 1},
    "A1": {"1": 2, "2": 3},
    "A2": {"1": 4, "2": 5},
    "A3": {"1": 6, "2": 7},
    "D0": {"1": 22, "2": 23},
    "D1": {"1": 24, "2": 25},
    "D2": {"1": 26, "2": 27},
    "D3": {"1": 5, "2": 6},
    "D4": {"1": 7, "2": 8},
    "D5": {"1": 10, "2": 11},
    "D6": {"1": 12, "2": 13},
    "D7": {"1": 15, "2": 16},
}


def get_pin_for_port(port_name, pin_number=1):
    assert(port_name in Port)
    assert(pin_number in (1, 2))

    return Port[port_name][str(pin_number)]


def validate_input(obj, **kwargs):
    hints = get_type_hints(obj)
    for attr_name, attr_type in hints.items():
        if attr_name == 'return':
            continue

        attr_type_arr = [attr_type]
        if hasattr(attr_type, '__args__'):
            attr_type_arr = attr_type.__args__

        has_errors = True
        for attr_subtype in attr_type_arr:
            # if we use a default value on the method, it won't be in kwargs
            if attr_name not in kwargs or isinstance(kwargs[attr_name], attr_subtype):
                has_errors = False
                break
        if has_errors:
            raise TypeError(f"Argument '{attr_name}' is not of type {attr_type}")


def type_check(decorator):
    @wraps(decorator)
    def wrapped_decorator(*args, **kwargs):
        # translate *args into **kwargs
        func_args = getfullargspec(decorator)[0]
        kwargs.update(dict(zip(func_args, args)))

        validate_input(decorator, **kwargs)
        return decorator(**kwargs)

    return wrapped_decorator
