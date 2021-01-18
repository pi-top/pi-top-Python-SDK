from pitopcommon.singleton import Singleton


class PortManager(metaclass=Singleton):
    def __init__(self, state={}):
        # TODO: if state not empty, reproduce it
        self.port_lookup = state

    def register_component(self, component_type, port, **kwargs):
        if self.port_lookup.get(port):
            raise Exception("Port is already in use")

        component = component_type(port, **kwargs)
        self.port_lookup[port] = component
        return component

    def register_component_instance(self, component_instance, port):
        if self.port_lookup.get(port):
            raise Exception("Port is already in use")
        self.port_lookup[port] = component_instance

    def drop_component(self, port):
        component = self.port_lookup.get(port)
        if component is not None:
            # this doesn't actually release the port
            component = None
            self.port_lookup[port] = None

    def get_component(self, port):
        return self.port_lookup.get(port)
