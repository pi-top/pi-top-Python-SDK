from pitop.system.peripherals import connected_plate
from pitop.robotics.drive_controller import DriveController

from pitopcommon.common_ids import FirmwareDeviceID


class SupportsDriving(DriveController):
    def __init__(self, motor_left_port, motor_right_port, **kwargs):
        try:
            if connected_plate() != FirmwareDeviceID.pt4_expansion_plate:
                raise Exception
            DriveController.__init__(self, motor_left_port, motor_right_port)
            if hasattr(self, "add_component"):
                self.add_component(self, "drive_controller")
        except Exception:
            print("No DriveController")
