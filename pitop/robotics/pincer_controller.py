from pitop.pma import ServoMotor
from pitop.system.port_manager import PortManager


class PincerController:

    def __init__(self, right_pincer_port="S0", left_pincer_port="S3"):
        self._right_pincer_servo = ServoMotor(right_pincer_port)
        self._left_pincer_servo = ServoMotor(left_pincer_port)
        self.__port_manager = PortManager()
        self.__port_manager.register_pma_component(self._right_pincer_servo)
        self.__port_manager.register_pma_component(self._left_pincer_servo)
