from pitop.battery import Battery
from pitop.camera import Camera
from pitop.miniscreen import Miniscreen
from pitop.system import device_type
from pitop.system.peripherals import connected_plate
from pitop.system.port_manager import PortManager
from pitop.robotics.drive_controller import DriveController
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


class SupportsAttachingPlates(PortManager):
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
            PanTiltController.__init__(self, servo_pan_port, servo_tilt_port)
        except Exception:
            self._pan_tilt_controller = None
            print("No PanTilt")


class SupportsDriving(DriveController):
    def __init__(self, left_motor_port, right_motor_port):
        try:
            DriveController.__init__(self, left_motor_port, right_motor_port)
        except Exception:
            print("No DriveController")
