from pitop.pma import ServoMotor, ServoMotorState
from pitop.system.port_manager import PortManager


class PincerController:

    def __init__(self, right_pincer_port="S0", left_pincer_port="S3"):
        self._right_pincer = ServoMotor(right_pincer_port)
        self._left_pincer = ServoMotor(left_pincer_port)
        self.__right_pincer_state = ServoMotorState()
        self.__left_pincer_state = ServoMotorState()
        self.__port_manager = PortManager()
        self.__port_manager.register_pma_component(self._right_pincer)
        self.__port_manager.register_pma_component(self._left_pincer)

    def close(self, speed: int = 100, angle: int = 0):
        self.__right_pincer_state.speed = speed
        self.__right_pincer_state.angle = angle
        self.__left_pincer_state.speed = speed
        self.__left_pincer_state.angle = angle
        self._right_pincer.state = self.__right_pincer_state
        self._left_pincer.state = self.__left_pincer_state

    def open(self, speed: int = 50, angle: int = 45):
        self.__right_pincer_state.speed = speed
        self.__right_pincer_state.angle = angle
        self.__left_pincer_state.speed = speed
        self.__left_pincer_state.angle = -angle
        self._right_pincer.state = self.__right_pincer_state
        self._left_pincer.state = self.__left_pincer_state
