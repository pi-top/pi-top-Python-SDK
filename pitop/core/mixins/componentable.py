import json

from .recreatable import Recreatable
from .stateful import Stateful


class Componentable(Stateful, Recreatable):
    def __init__(self, children=[], config_dict={}):
        Stateful.__init__(self, children)
        Recreatable.__init__(self, config_dict)

    @classmethod
    def from_dict(cls, config_dict):
        components_config = config_dict.pop("components", {})
        # Create main object
        main_obj = super().from_dict(config_dict)

        # Add components
        for name, config in components_config.items():
            try:
                component = super().from_dict(config)
                component.name = name
                main_obj.add_component(component)
            except Exception as e:
                print(f"Error recreating {name}: {e}")

        return main_obj

    @classmethod
    def from_file(cls, path):
        print(f"Loading configuration from {path}")
        with open(path) as json_file:
            config_dict = json.load(json_file)
        return cls.from_dict(config_dict)

    def add_component(self, component):
        self.children.append(component.name)
        setattr(self, component.name, component)

    @property
    def component_config(self):
        cfg = super().component_config
        cfg["components"] = {}
        for child_name in self.children:
            if hasattr(self, child_name):
                child_obj = getattr(self, child_name)
                if isinstance(child_obj, Recreatable):
                    cfg["components"][child_name] = child_obj.component_config
        return cfg

    def save_config(self, path):
        print(f"Storing configuration in {path}")
        with open(path, "w") as writer:
            json.dump(self.component_config, writer)
