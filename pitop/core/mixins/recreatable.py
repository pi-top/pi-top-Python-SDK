import importlib
import json


class Recreatable:
    """Represents an object that keeps track of a set of parameters that will
    allow to be recreate it in the future."""

    def __init__(self, config_dict={}):
        if not isinstance(config_dict, dict):
            raise TypeError("Argument must be a dictionary")

        self._config = config_dict
        self.add_to_config("classname", self.__class__.__name__)
        self.add_to_config("module", self.__module__)
        for k, v in config_dict.items():
            self.add_to_config(k, v)

    @classmethod
    def from_config(cls, config_dict):
        """Creates an instance of a Recreatable object with parameters in the
        provided dictionary."""
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
            config_dict = json.load(json_file)
        return cls.from_config(config_dict)

    def save_config(self, path):
        """Stores the set of parameters to recreate an object in a JSON
        file."""
        print(f"Storing configuration in {path}")
        with open(path, "w") as writer:
            json.dump(self.component_config, writer, indent=4)

    def add_to_config(self, parameter, value):
        """Adds a parameter and value to the list of internal parameters to
        recreate an object."""
        self._config[parameter] = value

    @property
    def component_config(self):
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
        print(json.dumps(self.component_config, indent=4))
