from simple_pid import PID
import math


class DrivingManager:
    class PIDManager:
        def __init__(self):
            self._Ki = 0.1
            self._Kd = 0.1
            self.distance = PID(Kp=0.0,
                                Ki=self._Ki,
                                Kd=self._Kd,
                                setpoint=0.0,
                                output_limits=(-1.0, 1.0)
                                )
            self.heading = PID(Kp=0.0,
                               Ki=self._Ki,
                               Kd=self._Kd,
                               setpoint=0.0,
                               output_limits=(-1.0, 1.0)
                               )

        def reset(self):
            self.heading.reset()
            self.distance.reset()

        def distance_update(self, deceleration_distance):
            self.distance.Kp = 1.0 / deceleration_distance

        def heading_update(self, deceleration_angle):
            self.heading.Kp = 1.0 / deceleration_angle

    def __init__(self,
                 max_motor_speed,
                 max_angular_speed,
                 full_speed_deceleration_distance=0.4,
                 full_speed_deceleration_angle=120.0
                 ):
        self._max_motor_speed = max_motor_speed  # m/s
        self._max_angular_speed = max_angular_speed  # rad/s
        self._max_deceleration_distance = full_speed_deceleration_distance  # m
        self._max_deceleration_angle = full_speed_deceleration_angle  # degrees

        self.linear_speed_factor = None
        self.angular_speed_factor = None
        self.max_velocity = None
        self.max_angular_velocity = None
        self.deceleration_distance = None
        self.deceleration_angle = None
        self.pid = self.PIDManager()

    def update_linear_speed(self, speed_factor):
        self.linear_speed_factor = speed_factor
        self.max_velocity = self.linear_speed_factor * self._max_motor_speed
        self.deceleration_distance = self.linear_speed_factor * self._max_deceleration_distance
        self.pid.distance_update(deceleration_distance=self.deceleration_distance)

    def update_angular_speed(self, speed_factor):
        self.angular_speed_factor = speed_factor
        self.max_angular_velocity = self.angular_speed_factor * self._max_angular_speed
        self.deceleration_angle = self.angular_speed_factor * math.radians(self._max_deceleration_angle)
        self.pid.heading_update(deceleration_angle=self.deceleration_angle)
