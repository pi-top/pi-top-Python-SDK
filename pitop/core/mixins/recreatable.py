class Recreatable:
    def __init__(self, config_dict={}):
        self._config = config_dict
        self.add_to_config("classname", self.__class__.__name__)
        for k, v in config_dict.items():
            self.add_to_config(k, v)

    def add_to_config(self, key, value):
        self._config[key] = value

    @property
    def component_config(self):
        cfg = {}
        for k, v in self._config.items():
            if callable(v):
                cfg[k] = v()
            else:
                cfg[k] = v
        return cfg
