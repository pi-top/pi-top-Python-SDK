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

class FeedbackController:
    def __init__(self, chassis_speed_x, drive_controller):
        self._chassis_move_controller = drive_controller
        self._pid = PID(Kp=0.045, Ki=0.002, Kd=0.0035, setpoint=0)
        self._pid.output_limits = (-5.0, 5.0)
        self._twist_data = Twist()
        self._twist_data.angular.z = 0
        self._twist_data.linear.x = chassis_speed_x

    def stop_chassis(self):
        self._twist_data.linear.x = 0
        self._twist_data.angular.z = 0
        self._chassis_move_controller.command(self._twist_data)

    def control_update(self, state):
        control_effort = self._pid(state)
        self.send_motor_commands(control_effort)

    def send_motor_commands(self, control_effort):
        self._twist_data.angular.z = control_effort
        self._chassis_move_controller.command(self._twist_data)

    @property
    def speed_linear_x(self):
        return self._twist_data.linear.x

    @speed_linear_x.setter
    def speed_linear_x(self, speed_linear_x):
        self._twist_data.linear.x = speed_linear_x
