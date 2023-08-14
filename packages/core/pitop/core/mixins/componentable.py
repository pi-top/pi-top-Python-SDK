from .recreatable import Recreatable
from .stateful import Stateful


class Componentable(Stateful, Recreatable):
    """Represents an object that attach components to itself, and that can
    store its internal configuration to recreate itself in the future."""

    def __init__(self, children=None, config_dict=None):
        if config_dict is None:
            config_dict = dict()

        Stateful.__init__(self, children)
        Recreatable.__init__(self, config_dict)

    def __del__(self):
        self.close()

    def children_gen(self):
        if not hasattr(self, "children"):
            return
        for child_name in self.children:
            if hasattr(self, child_name):
                child = getattr(self, child_name)
                yield child_name, child

    def close(self):
        def closeable(obj):
            return callable(getattr(obj, "close", None))

        for _, child in self.children_gen():
            if closeable(child):
                child.close()

        if closeable(super()):
            super().close()

    @classmethod
    def from_config(cls, config_dict):
        """Creates an instance of a :class:`Componentable` using the provided
        dictionary.

        If a component fails to be recreated, the main object will still
        be created, but without it.
        """
        components_config = config_dict.pop("components", dict())
        # Create main object
        main_obj = super().from_config(config_dict)

        # Add components
        for name, config in components_config.items():
            try:
                component = super().from_config(config)
                component.name = name
                main_obj.add_component(component)
            except Exception as e:
                print(f"Error recreating {name}: {e}")

        return main_obj

    def add_component(self, component, name=""):
        """Attaches a component to the current instance as an attribute. It can
        be accessed using the component name or the name provided in the
        arguments.

        Note that even though non native pi-top components can be
        added to a instance, only components that inherit from
        :class:`Recreatable` will be displayed in the :prop:`config`.
        """
        is_recreatable = isinstance(component, Recreatable)

        if not is_recreatable and not name:
            raise AttributeError("A name must be provided to add this component.")
        if name and not isinstance(name, str):
            raise AttributeError("Name must be a string")

        if name and is_recreatable:
            component.name = name
            component._config["name"] = name

        component_name = component.name if is_recreatable else name
        if component_name in self.children:
            raise AttributeError(
                f"There's already a component with the name '{component_name}' registered."
            )

        self.children.append(component_name)
        setattr(self, component_name, component)

    @property
    def config(self):
        """Returns the component configuration as a dictionary."""
        cfg = super().config
        cfg["components"] = dict()
        for name, child in self.children_gen():
            if isinstance(child, Recreatable):
                cfg["components"][name] = child.config
        return cfg
