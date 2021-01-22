from simple_pid import PID

from pitop.processing.utils.twist import Twist


# // short guide for tuning PIDs \\ #
# a) Set integral and derivative gains to zero (work only with the P part).
#
# b) Vary this proportional gain until you obtain the best possible performance.
#
# c) Keeping this prop. gain, now vary the integral gain. This fact will reduce
# the steady state error but (as expected) it may introduce some oscillations and overshoot. Select the best one like
# this.
#
# d) You should have obtained a fast response system but with (possibly) high overshot and oscillations. Now,
# keeping fixed the above mentioned gains, vary the derivative gain. This will damp your system reducing oscillations
# and overshoot. Naturally, this new variation may affect the general performance but try to select the best deriv.
# gain.
#
# e) Return to step (a) in order to improve your closed loop performance as best as possible.

class PIDController:
    def __init__(self, linear_speed):
        self.__pid = PID(Kp=0.045, Ki=0.002, Kd=0.0035, setpoint=0)
        self.__pid.output_limits = (-5.0, 5.0)

        self.__twist_data = Twist()

        self.__twist_data.angular.z = 0
        self.__twist_data.linear.x = linear_speed

    def stop(self):
        self.__twist_data.linear.x = 0
        self.__twist_data.angular.z = 0

    def set_target_control_angle(self, target_angle):
        self.__twist_data.angular.z = self.__pid(target_angle)

    @property
    def twist(self):
        return self.__twist_data

    @property
    def speed_linear_x(self):
        return self.__twist_data.linear.x

    @speed_linear_x.setter
    def speed_linear_x(self, speed_linear_x):
        self.__twist_data.linear.x = speed_linear_x

    @property
    def _speed_angular_z(self):
        return self.__twist_data.angular.z

    @_speed_angular_z.setter
    def _speed_angular_z(self, _speed_angular_z):
        self.__twist_data.angular.z = _speed_angular_z
