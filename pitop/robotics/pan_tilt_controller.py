from pitop.pma import ServoMotor
from pitop.system.port_manager import PortManager


class PanTiltController:

    def __init__(self, servo_pan_port="S0", servo_tilt_port="S3"):
        self._pan_servo = ServoMotor(servo_pan_port)
        self._tilt_servo = ServoMotor(servo_tilt_port)
        self.__port_manager = PortManager()
        self.__port_manager.register_pma_component(self._pan_servo)
        self.__port_manager.register_pma_component(self._tilt_servo)
