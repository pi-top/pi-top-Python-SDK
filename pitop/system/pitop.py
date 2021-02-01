from pitop.battery import Battery
from pitop.miniscreen import Miniscreen
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
        self._battery = None
        self._miniscreen = None
        self._port_manager = None
        self._plate = None

        device = device_type()
        if device != DeviceName.pi_top_ceed.value:
            self._battery = Battery()

        if device == DeviceName.pi_top_4.value:
            self._miniscreen = Miniscreen()
            self._port_manager = PortManager(state={})
            self._plate = connected_plate()

    @property
    def battery(self):
        """
        If not using a pi-topCEED, it returns a :class:`pitop.battery.Battery` object to interact with
        the miniscreen OLED display.

        This will return None if on a pi-topCEED.
        """
        return self._battery

    @property
    def miniscreen(self):
        """
        If using a pi-top [4], it returns a :class:`pitop.miniscreen.Miniscreen` object to interact with
        the miniscreen OLED display.

        This will return None if not on a pi-top [4].
        """
        return self._miniscreen

    @property
    def oled(self):
        """
        .. warning::
            This property is deprecated and will be deleted on the next major release of the SDK.

        If using a pi-top [4], it returns a :class:`pitop.miniscreen.Miniscreen` object to interact with
        the miniscreen OLED display.

        This will return None if not on a pi-top [4].
        """
        return self._miniscreen

    @property
    def up_button(self):
        """
        If using a pi-top [4], it returns a :class:`pitop.miniscreen.MiniscreenButton` object to interact with
        the miniscreen up button.

        This will return None if not on a pi-top [4].
        """
        return self._miniscreen.up_button

    @property
    def down_button(self):
        """
        If using a pi-top [4], it returns a :class:`pitop.miniscreen.MiniscreenButton` object to interact with
        the miniscreen down button.

        This will return None if not on a pi-top [4].
        """
        return self._miniscreen.down_button

    @property
    def select_button(self):
        """
        If using a pi-top [4], it returns a :class:`pitop.miniscreen.MiniscreenButton` object to interact with
        the miniscreen select button.

        This will return None if not on a pi-top [4].
        """

        return self._miniscreen.select_button

    @property
    def cancel_button(self):
        """
        If using a pi-top [4], it returns a :class:`pitop.miniscreen.MiniscreenButton` object to interact with
        the miniscreen cancel button.

        This will return None if not on a pi-top [4].
        """
        return self._miniscreen.cancel_button

    def register_pma_component(self, component_instance):
        """
        If using a pi-top [4], register a PMA component as being connected. This allows
        the object to keep track of what component is connected and where.

        This will return None if not on a pi-top [4].

        :param component_instance: Instance of a PMA component.
        """
        self._port_manager.register_pma_component(component_instance)

    def drop_pma_component(self, port):
        """
        If using a pi-top [4], unregister a PMA component as being connected. This will free
        the port to be reused if necessary.

        This will return None if not on a pi-top [4].

        :param str port: name of the PMA port where the component to be dropped is connected.
        """
        self._port_manager.drop_pma_component(port)

    def get_component_on_pma_port(self, port):
        """
        If using a pi-top [4], get the instance of the PMA component connected to a given port.

        This will return None if not on a pi-top [4].

        :param str port: name of the PMA port where the component to be retrieved is connected.
        """
        self._port_manager.get_component_on_pma_port(port)
