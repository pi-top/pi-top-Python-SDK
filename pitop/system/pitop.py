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
    """
    Abstraction of a pi-top device.

    When creating a PiTop object, a set of attributes will be set,
    depending on the pi-top device that it's running the code. For example, if run on
    a pi-top [4], an `oled` attribute will be created as an interface to control the
    miniscreen OLED display, but that won't be available for other pi-top devices.

    The PiTop class is a Singleton. This means that only one instance per process will
    be created. In practice, this means that if in a particular project you instance a PiTop
    class in 2 different files, they will share the internal state: you should be able to
    register components in one file (using :meth:`register_pma_component`) and retrieve
    it to use it in another file (using :meth:`get_component_on_pma_port`).
    """

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
        """
        Registers a PMA component to the pi-top device. This allows the object to keep
        track of what component is connected and where.

        :param component_instance: Instance of a PMA component.
        """
        if self._port_manager:
            self._port_manager.register_pma_component(component_instance)

    def drop_pma_component(self, port):
        """
        Unregisters a PMA component from the pi-top device. This will free the port
        to be reused if necessary.

        :param str port: name of the PMA port where the component to be dropped is connected.
        """
        if self._port_manager:
            self._port_manager.drop_pma_component(port)

    def get_component_on_pma_port(self, port):
        """
        Returns the instance of the PMA component connected to a given port.

        :param str port: name of the PMA port where the component to be retrieved is connected.
        """
        if self._port_manager:
            return self._port_manager.get_component_on_pma_port(port)
