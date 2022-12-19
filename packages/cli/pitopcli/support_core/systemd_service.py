from ..formatter import StdoutFormat


class SystemdService:
    def __init__(self):
        self._name = ""
        self._load_state = ""
        self._active_state = ""
        self._enabled = ""
        self._description = ""
        self._fragment_path = ""
        self._vendor_preset = ""
        self._sub_state = ""
        self._active_enter_timestamp = ""

    @classmethod
    def from_lines(cls, lines):
        service = cls()
        for line in lines:
            if "Id=" in line:
                service.name = line.replace("Id=", "")
            elif "LoadState=" in line:
                service.load_state = line.replace("LoadState=", "")
            elif "ActiveState=" in line:
                service.active_state = line.replace("ActiveState=", "")
            elif "UnitFileState=" in line:
                service.enabled = line.replace("UnitFileState=", "")
            elif "Description=" in line:
                service.description = line.replace("Description=", "")
            elif "UnitFilePreset=" in line:
                service.vendor_preset = line.replace("UnitFilePreset=", "")
            elif "FragmentPath=" in line:
                service.fragment_path = line.replace("FragmentPath=", "")
            elif "SubState=" in line:
                service.sub_state = line.replace("SubState=", "")
            elif "ActiveEnterTimestamp=" in line:
                service.active_enter_timestamp = line.replace(
                    "ActiveEnterTimestamp=", ""
                )
        return service

    @property
    def name(self):
        return self._name

    @property
    def load_state(self):
        return self._load_state

    @property
    def active_state(self):
        return self._active_state

    @property
    def enabled(self):
        return self._enabled

    @property
    def description(self):
        return self._description

    @property
    def vendor_preset(self):
        return self._vendor_preset

    @property
    def fragment_path(self):
        return self._fragment_path

    @property
    def sub_state(self):
        return self._sub_state

    @property
    def active_enter_timestamp(self):
        return self._active_enter_timestamp

    @name.setter
    def name(self, value):
        self._name = value.strip(" \t\n\r").replace(".service", "")

    @load_state.setter
    def load_state(self, value):
        self._load_state = value.strip(" \t\n\r")

    @active_state.setter
    def active_state(self, value):
        self._active_state = value.strip(" \t\n\r")

    @enabled.setter
    def enabled(self, value):
        self._enabled = value.strip(" \t\n\r")

    @description.setter
    def description(self, value):
        self._description = value.strip(" \t\n\r")

    @vendor_preset.setter
    def vendor_preset(self, value):
        self._vendor_preset = value.strip(" \t\n\r")

    @fragment_path.setter
    def fragment_path(self, value):
        self._fragment_path = value.strip(" \t\n\r")

    @sub_state.setter
    def sub_state(self, value):
        self._sub_state = value.strip(" \t\n\r")

    @active_enter_timestamp.setter
    def active_enter_timestamp(self, value):
        self._active_enter_timestamp = value.strip(" \t\n\r")

    def ____get_loaded_line(self):
        line = f"Loaded: {self.format_service(self.load_state)}"
        if self.load_state != "masked":
            line += f" ({self.fragment_path}; {self.format_service(self.enabled)}; vendor preset: {self.vendor_preset})"
        return line

    def __get_active_line(self):
        line = f"Active: {self.format_service(self.active_state)} ({self.format_service(self.sub_state)})"
        if self.active_state == "active":
            line += f" since {self.active_enter_timestamp}"
        return line

    @classmethod
    def format_service(cls, input_string):
        if input_string.strip(" \t\n\r") in ("loaded", "active", "enabled", "running"):
            return StdoutFormat.GREEN + input_string + StdoutFormat.ENDC
        elif input_string.strip(" \t\n\r") in (
            "inactive",
            "disabled",
            "exited",
            "dead",
        ):
            return StdoutFormat.DIM + input_string + StdoutFormat.ENDC
        return StdoutFormat.RED + input_string + StdoutFormat.ENDC

    def print(self):
        StdoutFormat.print_line(
            f"{StdoutFormat.bold(self.name)} ({self.description})", level=2
        )
        StdoutFormat.print_line(self.____get_loaded_line(), level=3)
        StdoutFormat.print_line(self.__get_active_line(), level=3)
