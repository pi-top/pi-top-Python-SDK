from pitopcommon.singleton import Singleton


class PortManager(metaclass=Singleton):
    def __init__(self, state=dict()):
        # TODO: if state not empty, reproduce it
        self.__pma_port_lookup = state

    def get_component_on_pma_port(self, port):
        # Return None if not available
        return self.__pma_port_lookup.get(port)

    def register_pma_component(self, component_instance):
        if not hasattr(component_instance, "_pma_port"):
            raise Exception(f"Component {component_instance} does not appear to be a PMA component")

        if self.get_component_on_pma_port(component_instance._pma_port):
            raise Exception(f"Port {component_instance._pma_port} is already in use")

        self.__pma_port_lookup[component_instance._pma_port] = component_instance

    def drop_pma_component(self, port):
        component_instance = self.get_component_on_pma_port(port)
        if component_instance is None:
            print(f"No component_instance found on port {port} - cannot drop from PortManager")
            return

        if hasattr(component_instance, "close"):
            component_instance.close()

        component_instance = None
        self.__pma_port_lookup[component_instance._pma_port] = None
