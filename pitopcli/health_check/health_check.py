from netifaces import (
    AF_LINK,
    AF_INET,
    AF_INET6,
    ifaddresses,
    interfaces,
)
from os import path, uname
from time import asctime, gmtime

from ..formatter import StdoutFormat
from .ptsoftware import PiTopSoftware
from .hub_communication import HubCommunication

from pitopcommon.command_runner import run_command


class HealthCheck:

    RASPI_CONFIG_SETTINGS = {
        "get_can_expand": {
            "description": "Filesystem can be expanded?",
            "type": bool,
        },
        "get_boot_cli": {
            "description": "Boot to CLI?",
            "type": bool,
        },
        "get_autologin": {
            "description": "Autologin?",
            "type": bool,
        },
        "get_boot_wait": {
            "description": "Boot waits until a network connection is established?",
            "type": bool,
        },
        "get_boot_splash": {
            "description": "Show splash screen at boot?",
            "type": bool,
        },
        "get_overscan": {
            "description": "Compensation for displays with overscan?",
            "type": bool,
        },
        "get_camera": {
            "description": "Camera interface enabled?",
            "type": bool,
        },
        "get_ssh": {
            "description": "SSH interface enabled?",
            "type": bool,
        },
        "get_vnc": {
            "description": "VNC interface enabled?",
            "type": bool,
        },
        "get_spi": {
            "description": "SPI interface enabled?",
            "type": bool,
        },
        "get_i2c": {
            "description": "I2C interface enabled?",
            "type": bool,
        },
        "get_serial": {
            "description": "Login shell accessible over serial?",
            "type": bool,
        },
        "get_serial_hw": {
            "description": "Serial interface is enabled?",
            "type": bool,
        },
        "get_onewire": {
            "description": "One-wire interface enabled?",
            "type": bool,
        },
        "get_rgpio": {
            "description": "GPIO server to be accessible over the network?",
            "type": bool,
        },
    }

    NETWORK_ENUM_LOOKUP = {AF_LINK: 'LINK LAYER',
                           AF_INET: 'IPv4',
                           AF_INET6: 'IPv6'}

    def run(self):
        StdoutFormat.print_header("SYSTEM HEALTH CHECK")
        print(f"Current time (GMT): {asctime(gmtime())}")
        print("")

        StdoutFormat.print_section("OS Information")
        print("")
        self.print_uname_output()
        print("")
        self.print_if_pitopOS()

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

        StdoutFormat.print_subsection("APT Sources")
        pt_sw.print_apt_sources()
        print("")

        StdoutFormat.print_section("pi-top Hardware")
        print("")
        try:
            hub = HubCommunication()
            hub.print_hub_registers()
        except Exception as e:
            print(f"{e}")

    def print_uname_output(self):
        u = uname()
        StdoutFormat.print_subsection("General Information")
        StdoutFormat.print_line(f"Kernel Name: {u.sysname}")
        StdoutFormat.print_line(f"Hostname: {u.nodename}")
        StdoutFormat.print_line(f"Kernel Version: {u.release}")
        StdoutFormat.print_line(f"Kernel Release: {u.version}")
        StdoutFormat.print_line(f"Platform: {u.machine}")

    def print_if_pitopOS(self):
        ptissue_path = "/etc/pt-issue"
        if not path.exists(ptissue_path):
            return
        data = {}
        with open(ptissue_path, 'r') as reader:
            for line in reader.readlines():
                content = line.split(":")
                if len(content) == 2:
                    data[content[0].strip()] = content[1].strip()
        StdoutFormat.print_subsection("pi-topOS Information")
        for k, v in data.items():
            StdoutFormat.print_line(f"{k}: {v}")
        print("")

    def print_raspi_config_settings(self):
        def get_setting_value(setting):
            try:
                return run_command(f"raspi-config nonint {setting}", timeout=5).strip()
            except Exception:
                return "Error getting setting"

        for setting, setting_dict in self.RASPI_CONFIG_SETTINGS.items():
            setting_value = get_setting_value(setting)
            if setting_dict.get("type"):
                setting_value = setting_dict.get("type")(setting_value)
            StdoutFormat.print_line(f"{StdoutFormat.bold(setting_dict.get('description'))} {setting_value}")

    def print_network_settings(self):
        def print_interface_info(interface_name):
            iface_info = ifaddresses(interface_name)
            # get network layer, ipv4 and ipv6 info for the provided interface
            for netiface_enum, address_family in self.NETWORK_ENUM_LOOKUP.items():
                interface_info = iface_info.get(netiface_enum)
                if not interface_info:
                    continue

                # Print interface information for a particular "address family"
                StdoutFormat.print_line(f"{address_family}")
                for address_number, address_info in enumerate(interface_info):
                    # An interface can have more than one address associated to it
                    if len(interface_info) > 1:
                        StdoutFormat.print_line(f"Subaddress #{address_number + 1}",
                                                level=2)
                    # Print interface attributes & values for the address
                    for addr_attribute, addr_attribute_value in address_info.items():
                        StdoutFormat.print_line(f"{addr_attribute}: {addr_attribute_value}",
                                                level=3 if len(interface_info) > 1 else 2)

        interfaces_list = interfaces()
        for iface in interfaces_list:
            StdoutFormat.print_subsection(f"Interface: {StdoutFormat.bold(iface)}")
            print_interface_info(iface)
