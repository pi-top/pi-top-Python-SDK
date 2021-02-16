from pitop.battery import Battery
from pitop.camera import Camera
from pitop.miniscreen import Miniscreen
from pitop.pma import (
    EncoderMotor,
    ForwardDirection,
    ServoMotor,
)
from pitop.system import device_type
from pitop.system.peripherals import connected_plate
from pitop.system.port_manager import PortManager
from pitop.robotics.drive_controller import DriveBase
from pitop.robotics.pan_tilt_controller import PanTiltController

from pitopcommon.common_ids import FirmwareDeviceID
from pitopcommon.common_names import DeviceName


class SupportsMiniscreen():
    def __init__(self):
        self._miniscreen = None
        if device_type() == DeviceName.pi_top_4.value:
            self._miniscreen = Miniscreen()

    @property
    def miniscreen(self):
        if self._miniscreen:
            return self._miniscreen
        raise Exception("No miniscreen")

    @property
    def oled(self):
        if self._miniscreen:
            return self._miniscreen
        raise Exception("No miniscreen")


class SupportsBattery():
    def __init__(self):
        self._battery = None
        if device_type() != DeviceName.pi_top_ceed.value:
            self._battery = Battery()

    @property
    def battery(self):
        if self._battery:
            return self._battery
        raise Exception("No battery")


class ManagesPMAComponents(PortManager):
    def __init__(self):
        if device_type() == DeviceName.pi_top_4.value:
            PortManager.__init__(self)


class SupportsCamera():
    def __init__(self, index, resolution):
        try:
            self._camera = Camera(index, resolution)
        except Exception:
            self._camera = None
            print("No camera")

    @property
    def camera(self):
        if self._camera:
            return self._camera
        raise Exception("Camera not available")


class SupportsPanTilt(PanTiltController):
    def __init__(self, servo_pan_port, servo_tilt_port):
        try:
            port_manager = PortManager()
            pan_servo = port_manager.get_or_create_pma_component(ServoMotor, servo_pan_port)
            tilt_servo = port_manager.get_or_create_pma_component(ServoMotor, servo_tilt_port)
            PanTiltController.__init__(self, pan_servo, tilt_servo)
        except Exception:
            self._pan_tilt_controller = None
            print("No PanTilt")


class SupportsDriving(DriveBase):
    def __init__(self, left_motor_port, right_motor_port):
        try:
            port_manager = PortManager()
            left_motor = port_manager.get_or_create_pma_component(EncoderMotor,
                                                                  left_motor_port,
                                                                  forward_direction=ForwardDirection.CLOCKWISE)
            right_motor = port_manager.get_or_create_pma_component(EncoderMotor,
                                                                   right_motor_port,
                                                                   forward_direction=ForwardDirection.COUNTER_CLOCKWISE)
            DriveBase.__init__(self, left_motor, right_motor)
        except Exception:
            print("No DriveBase")
