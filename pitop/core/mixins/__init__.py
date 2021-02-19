from pitop.battery import Battery
from pitop.camera import Camera
from pitop.miniscreen import Miniscreen
from pitop.system import device_type
from pitop.system.peripherals import connected_plate
from pitop.system.component_manager import ComponentManager
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


class ManagesPMAComponents(ComponentManager):
    def __init__(self):
        if device_type() == DeviceName.pi_top_4.value:
            ComponentManager.__init__(self)


class SupportsCamera():
    def __init__(self, camera_device_index, camera_resolution, **kwargs):
        try:
            self._camera = Camera(camera_device_index, camera_resolution)
        except Exception:
            self._camera = None
            print("No camera")

    @property
    def camera(self):
        if self._camera:
            return self._camera
        raise Exception("Camera not available")


class SupportsPanTilt(PanTiltController):
    def __init__(self, servo_pan_port, servo_tilt_port, **kwargs):
        try:
            PanTiltController.__init__(self, servo_pan_port, servo_tilt_port)
            if hasattr(self, "add_component"):
                self.add_component(self, "pan_tilt_controller")
        except Exception:
            self._pan_tilt_controller = None
            print("No PanTilt")


class SupportsDriving(DriveController):
    def __init__(self, motor_left_port, motor_right_port, **kwargs):
        try:
            DriveController.__init__(self, motor_left_port, motor_right_port)
            if hasattr(self, "add_component"):
                self.add_component(self, "drive_controller")
        except Exception:
            print("No DriveController")
