from os import listdir
from subprocess import check_output

from ..formatter import StdoutFormat


class Service:
    def __init__(self):

        self._name = ""
        self._load_state = ""
        self._active_state = ""
        self._enabled = ""

    def set_name(self, value):
        self._name = value.strip(" \t\n\r")

    def set_load_state(self, value):
        self._load_state = value.strip(" \t\n\r")

    def set_active_state(self, value):
        self._active_state = value.strip(" \t\n\r")

    def set_enabled(self, value):
        self._enabled = value.strip(" \t\n\r")

    def name(self):
        return self._name

    def load_state(self):
        return self._load_state

    def active_state(self):
        return self._active_state

    def enabled(self):
        return self._enabled


class PtSystemdServices:
    def format_service(self, input_string):
        if input_string.strip(" \t\n\r") in ("loaded", "active", "enabled"):
            return StdoutFormat.GREEN + input_string + StdoutFormat.ENDC
        elif input_string.strip(" \t\n\r") in ("inactive", "disabled"):
            return StdoutFormat.DIM + input_string + StdoutFormat.ENDC
        return StdoutFormat.RED + input_string + StdoutFormat.ENDC

    def print_pt_systemd_status(self):
        pt_service_names = self.get_pt_systemd_services()
        services = []

        for service_name in pt_service_names:
            output = check_output(
                [
                    "systemctl",
                    "show",
                    service_name,
                    "--full",
                    "--no-legend",
                    "--lines=0",
                    "--no-pager",
                ]
            )
            output = output.decode("UTF-8")
            lines = output.split("\n")
            service = Service()

            for line in lines:
                if "Id=" in line:
                    service.set_name(line.replace("Id=", ""))
                elif "LoadState=" in line:
                    service.set_load_state(line.replace("LoadState=", ""))
                elif "ActiveState=" in line:
                    service.set_active_state(line.replace("ActiveState=", ""))
                elif "UnitFileState=" in line:
                    service.set_enabled(line.replace("UnitFileState=", ""))

            services.append(service)

        longest_service_name = 0
        longest_load_state = 0
        longest_active_state = 0
        longest_enabled = 0

        for service in services:
            if len(service.name()) > longest_service_name:
                longest_service_name = len(service.name())
            if len(service.load_state()) > longest_load_state:
                longest_load_state = len(service.load_state())
            if len(service.active_state()) > longest_active_state:
                longest_active_state = len(service.active_state())
            if len(service.enabled()) > longest_enabled:
                longest_enabled = len(service.enabled())

        for service in services:
            print(
                " └ "
                + StdoutFormat.bold(service.name().ljust(longest_service_name))
                + "  "
                + self.format_service(
                    service.load_state().ljust(longest_load_state)
                )
                + " "
                + self.format_service(service.enabled().ljust(longest_enabled))
                + " "
                + self.format_service(
                    service.active_state().ljust(longest_active_state)
                )
            )

    def get_pt_systemd_services(self):
        pt_service_names = []
        for systemd_service_file in sorted(listdir("/lib/systemd/system")):
            if systemd_service_file.startswith("pt-"):
                pt_service_names.append(systemd_service_file)
        return pt_service_names
