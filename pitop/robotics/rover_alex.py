from pitop import PiTop
from pitop.camera import Camera
from pitop.pma import (
    ServoMotor,
    UltrasonicSensor,
)

from pitopcommon.common_ids import FirmwareDeviceID

from .drive_controller import DriveController


class RoverAlex(PiTop):
    def __init__(self,
                 motor_left_port="M1",
                 motor_right_port="M2",
                 camera_port=0,
                 ultrasonic_sensor_port="D1",
                 servo_left_port="S1",
                 servo_right_port="S2"
                 ):

        super().__init__()
        if self._plate is None or self._plate != FirmwareDeviceID.pt4_expansion_plate:
            raise Exception("Expansion Plate not connected")

        self.camera = self.port_manager.register_component(Camera, camera_port)
        self.ultrasonic_sensor = self.port_manager.register_component(UltrasonicSensor, ultrasonic_sensor_port)
        self.servo_left = self.port_manager.register_component(ServoMotor, servo_left_port)
        self.servo_right = self.port_manager.register_component(ServoMotor, servo_right_port)

        self._drive_controller = DriveController(motor_left_port, motor_right_port)
        self.motor_left = self.port_manager.get_component(motor_left_port)
        self.motor_right = self.port_manager.get_component(motor_right_port)

    def forward(self, speed_factor):
        self._drive_controller.forward(speed_factor)

    def backward(self, speed_factor):
        self._drive_controller.backward(speed_factor)

    def left(self, speed_factor):
        self._drive_controller.left(speed_factor)

    def right(self, speed_factor):
        self._drive_controller.right(speed_factor)

    def stop(self):
        self._drive_controller.stop()
