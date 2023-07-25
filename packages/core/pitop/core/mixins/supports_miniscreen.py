from pitop.common.common_names import DeviceName
from pitop.core.exceptions import UnavailableComponent
from pitop.system import device_type


class SupportsMiniscreen:
    def __init__(self):
        self._miniscreen = None
        if device_type() == DeviceName.pi_top_4.value:
            from pitop.miniscreen import Miniscreen

            self._miniscreen = Miniscreen()

    @property
    def miniscreen(self):
        if self._miniscreen:
            return self._miniscreen
        raise UnavailableComponent("Miniscreen isn't available on this device")

    @property
    def oled(self):
        return self.miniscreen
