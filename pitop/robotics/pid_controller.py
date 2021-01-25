from simple_pid import PID


# TODO: decide whether to remove this and use simple_pid directly in drive_controller
class PIDController:
    def __init__(self, lower_limit, upper_limit, setpoint, Kp, Ki, Kd):
        self.__pid = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=setpoint)
        self.__pid.output_limits = (lower_limit, upper_limit)

    def control_state_update(self, state):
        control_output = self.__pid(state)
        return control_output
