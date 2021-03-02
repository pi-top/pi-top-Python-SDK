from pitop.robotics.pan_tilt_controller import PanTiltController
from pitop.system.peripherals import connected_plate

from pitopcommon.common_ids import FirmwareDeviceID


class SupportsPanTilt(PanTiltController):
    def __init__(self, servo_pan_port, servo_tilt_port, **kwargs):
        try:
            if connected_plate() != FirmwareDeviceID.pt4_expansion_plate:
                raise Exception
            PanTiltController.__init__(self, servo_pan_port, servo_tilt_port)
            if hasattr(self, "add_component"):
                self.add_component(self, "pan_tilt_controller")
        except Exception:
            self._pan_tilt_controller = None
            print("No PanTilt")
