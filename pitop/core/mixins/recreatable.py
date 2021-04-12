import importlib
from json import (
    dump,
    dumps,
    load,
)


class Recreatable:
    """Represents an object that keeps track of a set of parameters that will
    allow to be recreate it in the future.

    The values for each key provided in the :param:`config_dict`
    parameter can be a constant value or a reference to a function,
    which will be evaluated when the object configuration is requested.
    This is useful for cases where a parameter changes its value on
    runtime.
    """

    def __init__(self, config_dict=None):
        if config_dict is None:
            config_dict = dict()

        if not isinstance(config_dict, dict):
            raise TypeError("Argument must be a dictionary")

        config_dict.update({"classname": self.__class__.__name__,
                            "module": self.__module__,
                            "version": "0.17.0"})
        for k, v in config_dict.items():
            config_dict.update({k: v})

        self._config = config_dict

    @classmethod
    def from_config(cls, config_dict):
        """Creates an instance of a Recreatable object with parameters in the
        provided dictionary."""
        _ = config_dict.pop("version", None)
        cls_name = config_dict.pop("classname")
        module_name = config_dict.pop("module")

        message = f"Recreating {cls_name} (from {module_name})"
        message += f" with {config_dict}" if config_dict else ""
        print(message)

        main_cls = cls.import_class(module_name, cls_name)
        return main_cls(**config_dict)

    @classmethod
    def from_file(cls, path):
        """Creates an instance of an object using the JSON file from the
        provided path."""
        print(f"Loading configuration from {path}")
        with open(path) as json_file:
            config_dict = load(json_file)
        return cls.from_config(config_dict)

    def save_config(self, path):
        """Stores the set of parameters to recreate an object in a JSON
        file."""
        print(f"Storing configuration in {path}")
        with open(path, "w") as writer:
            dump(self.config, writer, indent=4)

    @property
    def config(self):
        """Returns a dictionary with the set of parameters that can be used to
        recreate an object."""
        cfg = {}
        for k, v in self._config.items():
            cfg[k] = v() if callable(v) else v
        return cfg

    @staticmethod
    def import_class(module_name, class_name):
        """Imports a class given a module and a class name."""
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def print_config(self):
        print(dumps(self.config, indent=4))
