import importlib
import json


class Recreatable:
    def __init__(self, config_dict={}):
        self._config = config_dict
        self.add_to_config("classname", self.__class__.__name__)
        self.add_to_config("module", self.__module__)
        for k, v in config_dict.items():
            self.add_to_config(k, v)

    @classmethod
    def from_dict(cls, config_dict):
        cls_name = config_dict.pop("classname")
        module_name = config_dict.pop("module")

        message = f"Recreating {cls_name} (from {module_name})"
        message += f" with {config_dict}" if config_dict else ""
        print(message)

        main_cls = cls.import_class(module_name, cls_name)
        return main_cls(**config_dict)

    @classmethod
    def from_file(cls, path):
        print(f"Loading configuration from {path}")
        with open(path) as json_file:
            config_dict = json.load(json_file)
        return cls.from_dict(config_dict)

    def save_config(self, path):
        print(f"Storing configuration in {path}")
        with open(path, "w") as writer:
            json.dump(self.component_config, writer, indent=4)

    def add_to_config(self, key, value):
        self._config[key] = value

    @property
    def component_config(self):
        cfg = {}
        for k, v in self._config.items():
            cfg[k] = v() if callable(v) else v
        return cfg

    @staticmethod
    def import_class(module_name, class_name):
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def print_config(self):
        print(json.dumps(self.component_config, indent=4))
