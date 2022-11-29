from pitop.common.common_names import DeviceName
from pitop.core.exceptions import UnavailableComponent
from pitop.system import device_type


class SupportsBattery:
    def __init__(self):
        from pitop.battery import Battery

        self._battery = None
        if device_type() != DeviceName.pi_top_ceed.value:
            self._battery = Battery()

    @property
    def battery(self):
        if self._battery:
            return self._battery
        raise UnavailableComponent("Battery isn't available on this device")
