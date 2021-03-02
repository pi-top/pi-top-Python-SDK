from .recreatable import Recreatable
from .stateful import Stateful


class Componentable(Stateful, Recreatable):
    def __init__(self, children=[], config_dict={}):
        Stateful.__init__(self, children)
        Recreatable.__init__(self, config_dict)

    def add_component(self, component):
        self.children.append(component.name)
        setattr(self, component.name, component)

    @property
    def component_config(self):
        cfg = super().component_config
        for child_name in self.children:
            if hasattr(self, child_name):
                child_obj = getattr(self, child_name)
                if isinstance(child_obj, Recreatable):
                    cfg[child_name] = child_obj.component_config
        return cfg
