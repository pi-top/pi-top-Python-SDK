from pitopcommon.singleton import Singleton


class PortManager(metaclass=Singleton):
    def __init__(self, state=dict()):
        # TODO: if state not empty, reproduce it
        self.__pma_port_lookup = state

    def get_component_on_pma_port(self, port):
        """
        If using a pi-top [4], get the instance of the PMA component connected to a given port.

        This will return None if not on a pi-top [4].

        :param str port: name of the PMA port where the component to be retrieved is connected.
        """
        # Return None if not available
        return self.__pma_port_lookup.get(port)

    def register_pma_component(self, component_instance):
        """
        If using a pi-top [4], register a PMA component as being connected. This allows
        the object to keep track of what component is connected and where.

        This will return None if not on a pi-top [4].

        :param component_instance: Instance of a PMA component.
        """
        if not hasattr(component_instance, "_pma_port"):
            raise Exception(f"Component {component_instance} does not appear to be a PMA component")

        if self.get_component_on_pma_port(component_instance._pma_port):
            raise Exception(f"Port {component_instance._pma_port} is already in use")

        self.__pma_port_lookup[component_instance._pma_port] = component_instance

    def drop_pma_component(self, port):
        """
        If using a pi-top [4], unregister a PMA component as being connected. This will free
        the port to be reused if necessary.

        This will return None if not on a pi-top [4].

        :param str port: name of the PMA port where the component to be dropped is connected.
        """
        component_instance = self.get_component_on_pma_port(port)
        if component_instance is None:
            print(f"No component_instance found on port {port} - cannot drop from PortManager")
            return

        if hasattr(component_instance, "close"):
            component_instance.close()

        component_instance = None
        self.__pma_port_lookup[component_instance._pma_port] = None

    def get_or_create_component(self, component=None, port=None, component_name=None):
        if hasattr(self, component_name):
            component_from_name = getattr(self, component_name)
            if component and not isinstance(component, component_from_name):
                raise Exception(f"Component {component_name} already exists but has a different type than the one provided")
            if port and port != component_from_name.port_name:
                raise Exception(f"Component {component_name} already exists but it's using a different port than the one provided")
            return component_from_name

        component_in_port = self.get_component_on_pma_port(port)
        if component_in_port:
            if component is None or isinstance(component, component_in_port):
                return component_in_port
            raise Exception(f"There's a component from a different type attached to the {port} port")

        if component and port:
            component_obj = component(port)
            self.register_pma_component(component_obj)
            return component_obj
