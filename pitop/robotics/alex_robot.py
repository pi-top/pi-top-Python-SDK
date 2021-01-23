from pitop import PiTop
from pitop.camera import Camera
from pitop.pma import (
    UltrasonicSensor
)

from pitopcommon.common_ids import FirmwareDeviceID

from .drive_controller import DriveController
from .pan_tilt_controller import PanTiltController


class AlexRobot(PiTop):
    def __init__(self,
                 motor_left_port="M3",
                 motor_right_port="M0",
                 camera_id=0,
                 ultrasonic_sensor_port="D3",
                 servo_pan_port="S0",
                 servo_tilt_port="S3"
                 ):

        super().__init__()
        if self._plate is None or self._plate != FirmwareDeviceID.pt4_expansion_plate:
            raise Exception("Expansion Plate not connected")

        self.camera = self.port_manager.register_component(Camera, camera_id)
        self.ultrasonic_sensor = self.port_manager.register_component(UltrasonicSensor, ultrasonic_sensor_port)

        self._drive_controller = DriveController(motor_left_port, motor_right_port)
        self.left_motor = self.port_manager.get_component(motor_left_port)
        self.right_motor = self.port_manager.get_component(motor_right_port)

        self._pan_tilt_controller = PanTiltController()
        self.pan_servo = self.port_manager.get_component(servo_pan_port)
        self.tilt_servo = self.port_manager.get_component(servo_tilt_port)

    def forward(self, speed_factor, hold=False):
        self._drive_controller.forward(speed_factor, hold)

    def backward(self, speed_factor, hold=False):
        self._drive_controller.backward(speed_factor, hold)

    def left(self, speed_factor, turn_radius=0):
        self._drive_controller.left(speed_factor, turn_radius)

    def right(self, speed_factor, turn_radius=0):
        self._drive_controller.right(speed_factor, turn_radius)

    def stop(self):
        self._drive_controller.stop()

    def target_lock_drive_angle(self, angle):
        self._drive_controller.target_lock_drive_angle(angle)

    def store_servo_zero_points(self):
        pass