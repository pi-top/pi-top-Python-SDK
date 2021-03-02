import importlib


class Recreatable:
    def __init__(self, config_dict={}):
        self._config = config_dict
        self.add_to_config("classname", self.__class__.__name__)
        self.add_to_config("module", self.__module__)
        for k, v in config_dict.items():
            self.add_to_config(k, v)

    def is_builtin_class_instance(self, obj):
        return obj.__class__.__module__ == '__builtin__'

    def add_to_config(self, key, value):
        self._config[key] = value

    @property
    def component_config(self):
        cfg = {}
        for k, v in self._config.items():
            cfg[k] = v() if callable(v) else v
        return cfg

    @classmethod
    def from_dict(cls, config_dict):
        cls_name = config_dict.pop("classname")
        module_name = config_dict.pop("module")

        message = f"Recreating {cls_name} (from {module_name})"
        message += f" with {config_dict}" if config_dict else ""
        print(message)

        main_cls = cls.import_class(module_name, cls_name)
        return main_cls(**config_dict)

    @staticmethod
    def import_class(module_name, class_name):
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
