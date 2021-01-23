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
    def __init__(self, lower_limit, upper_limit, setpoint, Kp, Ki, Kd):
        self.__pid = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=setpoint)
        self.__pid.output_limits = (lower_limit, upper_limit)

    def control_state_update(self, state):
        control_output = self.__pid(state)
        return control_output
