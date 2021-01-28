from pitop.battery import Battery
from pitop.miniscreen import (
    OLED,
    UpButton,
    DownButton,
    SelectButton,
    CancelButton,
)
from pitop.system import device_type
from pitop.system.peripherals import connected_plate
from pitop.system.port_manager import PortManager

from pitopcommon.common_names import DeviceName
from pitopcommon.singleton import Singleton


class PiTop(metaclass=Singleton):
    def __init__(self):
        is_pi_top_four = device_type() == DeviceName.pi_top_4.value

        self.battery = Battery()
        self.oled = OLED() if is_pi_top_four else None
        self.up_button = UpButton() if is_pi_top_four else None
        self.down_button = DownButton() if is_pi_top_four else None
        self.select_button = SelectButton() if is_pi_top_four else None
        self.cancel_button = CancelButton() if is_pi_top_four else None

        self._port_manager = PortManager(state={}) if is_pi_top_four else None
        self._plate = connected_plate() if is_pi_top_four else None

    def register_pma_component(self, component_instance):
        if self._port_manager:
            self._port_manager.register_pma_component(component_instance)

    def drop_pma_component(self, port):
        if self._port_manager:
            self._port_manager.drop_pma_component(port)

    def get_component_on_pma_port(self, port):
        if self._port_manager:
            return self._port_manager.get_component_on_pma_port(port)
