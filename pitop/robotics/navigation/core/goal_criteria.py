import math


class GoalCriteria:
    def __init__(
        self,
        full_speed_distance_error: float = 0.02,
        full_speed_angle_error: float = 3.0,
    ):
        self._full_speed_distance_error = full_speed_distance_error
        self._full_speed_angle_error = math.radians(full_speed_angle_error)

        self._max_distance_error = None
        self._max_angle_error = None
        self._starting_angle_error = None

    def angle(self, angle_error):
        if self._starting_angle_error is None:
            self._starting_angle_error = angle_error
        if abs(angle_error) < self._max_angle_error:
            self._starting_angle_error = None
            return True
        if self._starting_angle_error / (angle_error + 1e-6) < 0:
            # if the starting angle error is a different sign to the current angle error, then robot has overshot goal.
            # Consider goal to be reached to avoid trying to adjust angle at low angular speeds where starting friction
            # prevents precise movement
            self._starting_angle_error = None
            return True
        return False

    def distance(self, distance_error, angle_error):
        if abs(distance_error) < self._max_distance_error:
            return True
        if abs(angle_error) > math.pi / 2:
            # Overshot goal, error will be small so consider goal to be reached.
            # Otherwise robot would have to reverse a tiny amount which would be poor UX.
            # Robot will correct itself on subsequent navigation calls anyway.
            return True
        return False

    def update_linear_speed(self, speed_factor):
        self._max_distance_error = speed_factor * self._full_speed_distance_error

    def update_angular_speed(self, speed_factor):
        self._max_angle_error = speed_factor * self._full_speed_angle_error
