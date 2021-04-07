import math

MAX_LINEAR_SPEED = 0.44
MAX_ANGULAR_SPEED = 5.12
MAX_SERVO_ANGLE = 90


def calculate_direction(degree):
    direction = degree - 90

    # keeps direction between -180 and 180
    if direction > 180:
        return -(360 - direction)

    return direction


def calculate_pan_tilt_angle(data):
    angle = data.get('angle', {})
    degree = angle.get('degree', 0)
    distance = data.get('distance', 0)
    direction = calculate_direction(degree)

    return {
        'y': -math.cos(direction / 57.29) * distance * MAX_SERVO_ANGLE / 100.0,
        'z': math.sin(direction / 57.29) * distance * MAX_SERVO_ANGLE / 100.0,
    }


def calculate_velocity_twist(data):
    angle = data.get('angle', {})
    degree = angle.get('degree', 0)
    distance = data.get('distance', 0)
    direction = calculate_direction(degree)

    return {
        'linear': math.cos(direction / 57.29) * distance * MAX_LINEAR_SPEED / 100.0,
        'angular': math.sin(direction / 57.29) * distance * MAX_ANGULAR_SPEED / 100.0,
    }
