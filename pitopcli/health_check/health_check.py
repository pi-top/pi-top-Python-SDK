from os import uname
from netifaces import (
    AF_LINK,
    AF_INET,
    AF_INET6,
    ifaddresses,
    interfaces,
)

from ..formatter import StdoutFormat
from .ptsoftware import PiTopSoftware

from pitopcommon.command_runner import run_command


class HealthCheck:

    RASPI_CONFIG_SETTINGS = ("get_can_expand",
                             "get_hostname",
                             "get_boot_cli",
                             "get_autologin",
                             "get_boot_wait",
                             "get_boot_splash",
                             "get_overscan",
                             "get_camera",
                             "get_ssh",
                             "get_vnc",
                             "get_spi",
                             "get_i2c",
                             "get_serial",
                             "get_serial_hw",
                             "get_onewire",
                             "get_rgpio",
                             "get_pi_type",
                             "get_wifi_country")

    NETWORK_ENUM_LOOKUP = {AF_LINK: 'LINK LAYER',
                           AF_INET: 'IPv4',
                           AF_INET6: 'IPv6'}

    def print_os_info(self):
        print("")

        StdoutFormat.print_section("OS Information")
        self.print_machine_information()
        print("")

        StdoutFormat.print_section("raspi-config Settings")
        self.print_raspi_config_settings()
        print("")

        StdoutFormat.print_section("Network Settings")
        self.print_network_settings()
        print("")

        StdoutFormat.print_section("pi-top Software Information")
        print("")
        pt_sw = PiTopSoftware()
        StdoutFormat.print_subsection("pi-top Systemd Services")
        pt_sw.print_pt_systemd_status()
        print("")

        StdoutFormat.print_subsection("pi-top Installed Software")
        pt_sw.print_pt_installed_software()
        print("")

    def print_machine_information(self):
        u = uname()
        print(f"Kernel Name: {u.sysname}")
        print(f"Hostname: {u.nodename}")
        print(f"Kernel Version: {u.release}")
        print(f"Kernel Release: {u.version}")
        print(f"Platform: {u.machine}")

    def print_raspi_config_settings(self):
        def get_setting_value(setting):
            try:
                return run_command(f"raspi-config nonint {setting}", timeout=5).strip()
            except Exception:
                return "Error getting setting"

        for setting in self.RASPI_CONFIG_SETTINGS:
            print(f" └ {StdoutFormat.bold(setting)}: {get_setting_value(setting)}")

    def print_network_settings(self):
        def print_interface_info(interface_name):
            iface_info = ifaddresses(interface_name)
            # get network layer, ipv4 and ipv6 info
            for netiface_enum, section_name in self.NETWORK_ENUM_LOOKUP.items():
                interface_info = iface_info.get(netiface_enum)
                if interface_info:
                    for v in interface_info:
                        print(f" └ {section_name}: {v}")

        interfaces_list = interfaces()
        for iface in interfaces_list:
            StdoutFormat.print_subsection(f"Interface: {StdoutFormat.bold(iface)}")
            print_interface_info(iface)
