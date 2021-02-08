from apt import Cache
from os import listdir, walk, path
from re import search
from subprocess import check_output

from ..formatter import StdoutFormat


class Service:
    def __init__(self):

        self._name = ""
        self._load_state = ""
        self._active_state = ""
        self._enabled = ""
        self._description = ""

    def set_name(self, value):
        self._name = value.strip(" \t\n\r").replace(".service", "")

    def set_load_state(self, value):
        self._load_state = value.strip(" \t\n\r")

    def set_active_state(self, value):
        self._active_state = value.strip(" \t\n\r")

    def set_enabled(self, value):
        self._enabled = value.strip(" \t\n\r")

    def set_description(self, value):
        self._description = value.strip(" \t\n\r")

    def name(self):
        return self._name

    def load_state(self):
        return self._load_state

    def active_state(self):
        return self._active_state

    def enabled(self):
        return self._enabled

    def description(self):
        return self._description


class PiTopSoftware:
    def format_service(self, input_string):
        if input_string.strip(" \t\n\r") in ("loaded", "active", "enabled"):
            return StdoutFormat.GREEN + input_string + StdoutFormat.ENDC
        elif input_string.strip(" \t\n\r") in ("inactive", "disabled"):
            return StdoutFormat.DIM + input_string + StdoutFormat.ENDC
        return StdoutFormat.RED + input_string + StdoutFormat.ENDC

    def print_pt_systemd_status(self):
        services = self.get_pt_systemd_services()

        for active_state, services_arr in sorted(services.items()):
            StdoutFormat.print_line(f"{self.format_service(active_state)}")
            for service in services_arr:
                StdoutFormat.print_line(f"{StdoutFormat.bold(service.name())} ({service.description()})", level=2)
                StdoutFormat.print_line(f"Status: {self.format_service(service.load_state())}, {self.format_service(service.enabled())}", level=3)

    def get_pt_systemd_services(self):
        pt_service_names = self.get_pt_systemd_service_names()
        services = {}

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
                elif "Description=" in line:
                    service.set_description(line.replace("Description=", ""))

            active_state = service.active_state()
            if active_state not in services:
                services[active_state] = []
            services[active_state].append(service)

        return services

    def get_pt_systemd_service_names(self):
        pt_service_names = []
        for systemd_service_file in sorted(listdir("/lib/systemd/system")):
            if systemd_service_file.startswith("pt-"):
                pt_service_names.append(systemd_service_file)
        return pt_service_names

    def print_pt_installed_software(self):
        regex = "^pt-|-pt-|pitop|pi-top"
        apt_cache = Cache()

        pt_packages = []
        longest_package_name = 0
        longest_version = 0

        for pkg in apt_cache:
            match = search(regex, pkg.name)
            if apt_cache[pkg.name].is_installed and match:
                pt_packages.append((pkg.shortname, pkg.installed.version))
                if len(pkg.shortname) > longest_package_name:
                    longest_package_name = len(pkg.shortname)
                if len(pkg.installed.version) > longest_version:
                    longest_version = len(pkg.installed.version)

        for pkg_name, pkg_version in pt_packages:
            StdoutFormat.print_line(f"{pkg_name.ljust(longest_package_name)}" +
                                    " " +
                                    f"v{pkg_version.ljust(longest_version)}")

    def print_apt_sources(self):
        sources_directory = "/etc/apt/"

        for root, dirs, files in walk(sources_directory):
            for file in files:
                if file.endswith(".list"):
                    path_to_source = path.join(root, file)
                    StdoutFormat.print_line(path_to_source)

                    with open(path_to_source, 'r') as f:
                        lines = f.readlines()

                    for line in lines:
                        if not line.startswith("#"):
                            StdoutFormat.print_line(f"{line.strip()}", level=2)
