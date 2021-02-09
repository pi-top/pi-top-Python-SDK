from apt import Cache
from os import listdir, walk, path
from re import search
from subprocess import check_output

from ..formatter import StdoutFormat
from .systemd_service import SystemdService


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
                StdoutFormat.print_line(f"{StdoutFormat.bold(service.name)} ({service.description})", level=2)
                StdoutFormat.print_line(f"Status: {self.format_service(service.load_state)}, {self.format_service(service.enabled)}", level=3)

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
            service = SystemdService.from_lines(lines)

            active_state = service.active_state
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
        for pkg in apt_cache:
            match = search(regex, pkg.name)
            if apt_cache[pkg.name].is_installed and match:
                pt_packages.append((pkg.shortname, pkg.installed.version))

        StdoutFormat.print_table(pt_packages)

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
