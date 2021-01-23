from pitop.pma import ServoMotor
from pitop.system.port_manager import PortManager


class PanTiltController:

    def __init__(self, pan_servo_port="S0", tilt_servo_port="S3"):
        self._pan_servo = ServoMotor(pan_servo_port)
        self._tilt_servo = ServoMotor(tilt_servo_port)
        self.__port_manager = PortManager()
        self.__port_manager.register_component_instance(self._pan_servo, pan_servo_port)
        self.__port_manager.register_component_instance(self._tilt_servo, tilt_servo_port)

    def tilt_speed(self, speed):
        pass

    def pan_speed(self, speed):
        pass

    def tilt_angle(self, angle):
        pass

    def pan_angle(self, angle):
        pass



