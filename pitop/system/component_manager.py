from pitopcommon.singleton import Singleton
from pitop.system.pitop_component import PiTopComponent


class ComponentManager(metaclass=Singleton):
    def __init__(self, state=dict()):
        # TODO: if state not empty, reproduce it
        self.components = {}

    def add_component(self, instance, name):
        if not isinstance(name, str) or not name.isidentifier():
            raise Exception(f"Provided name {name} is invalid")
        if name in self.components or hasattr(self, name):
            raise Exception(f"Provided name {name} already exists")

        object_args = {}
        object_ports = []
        classname = ""
        if isinstance(instance, PiTopComponent):
            object_args = instance.args
            object_ports = instance.ports
            classname = instance.__class__.__name__

        for component_name, component in self.components.items():
            for port in object_ports:
                if port in component.get("ports"):
                    raise Exception(f"Port {port} is already in use by component {component_name}")

        component = {
            "instance": instance,
            "classname": classname,
            "ports": object_ports,
            "object_args": object_args
        }
        self.components[name] = component
        setattr(self, name, component.get("instance"))
