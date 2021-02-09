from netifaces import (
    AF_LINK,
    AF_INET,
    AF_INET6,
    ifaddresses,
    interfaces,
)
from distutils.util import strtobool
from os import path, uname
from time import strftime


from ..formatter import StdoutFormat
from .ptsoftware import PiTopSoftware
from .hub_communication import HubCommunication

from pitop.system import device_type
from pitopcommon.command_runner import run_command
from pitopcommon.common_names import DeviceName


def str_to_bool(value):
    return strtobool(value) == 0


class HealthCheck:

    RASPI_CONFIG_BOOT_SETTINGS = {
        "get_boot_cli": {
            "description": "Boot to Desktop?",
            "conversion_func": lambda x: not str_to_bool(x),
        },
        "get_autologin": {
            "description": "Autologin?",
            "conversion_func": str_to_bool,
        },
        "get_boot_wait": {
            "description": "Boot waits until a network connection is established?",
            "conversion_func": str_to_bool,
        },
        "get_boot_splash": {
            "description": "Show splash screen at boot?",
            "conversion_func": str_to_bool,
        },
    }

    RASPI_CONFIG_MISC = {
        "get_can_expand": {
            "description": "Filesystem can be expanded?",
            "conversion_func": str_to_bool,
        },
        "get_overscan": {
            "description": "Compensation for displays with overscan?",
            "conversion_func": str_to_bool,
        },
    }

    RASPI_CONFIG_INTERFACES = {
        "get_camera": {
            "description": "Camera interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_ssh": {
            "description": "SSH interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_vnc": {
            "description": "VNC interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_spi": {
            "description": "SPI interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_i2c": {
            "description": "I2C interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_serial": {
            "description": "Login shell accessible over serial?",
            "conversion_func": str_to_bool,
        },
        "get_serial_hw": {
            "description": "Serial interface is enabled?",
            "conversion_func": str_to_bool,
        },
        "get_onewire": {
            "description": "One-wire interface enabled?",
            "conversion_func": str_to_bool,
        },
        "get_rgpio": {
            "description": "GPIO server to be accessible over the network?",
            "conversion_func": str_to_bool,
        },
    }

    NETWORK_ENUM_LOOKUP = {AF_LINK: 'LINK LAYER',
                           AF_INET: 'IPv4',
                           AF_INET6: 'IPv6'}

    def run(self):
        StdoutFormat.print_header("SYSTEM HEALTH CHECK")
        print(f"Current time: {strftime('%a, %d %b %Y %I:%M:%S %p %Z')}")
        print("")

        StdoutFormat.print_section("Raspberry Pi Device Information")
        self.print_raspberry_pi_device_info()
        print("")

        StdoutFormat.print_section("System Information")
        self.print_debian_version()
        self.print_uname_output()
        self.print_if_pitopOS()
        print("")

        StdoutFormat.print_section("Interfaces (via raspi-config)")
        self.print_raspi_config_settings(self.RASPI_CONFIG_INTERFACES)
        print("")

        StdoutFormat.print_section("Boot Settings (via raspi-config)")
        self.print_raspi_config_settings(self.RASPI_CONFIG_BOOT_SETTINGS)
        print("")

        StdoutFormat.print_section("Misc (via raspi-config)")
        self.print_raspi_config_settings(self.RASPI_CONFIG_MISC)
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

        StdoutFormat.print_section("pi-top Device Information")
        try:
            hub = HubCommunication()
            hub.print_hub_registers()
        except Exception as e:
            print(f"{e}")

    def print_raspberry_pi_device_info(self):
        StdoutFormat.print_line(f"Device: {run_command('cat /proc/device-tree/model', timeout=2)}")
        StdoutFormat.print_line(f"Architecture: {uname().machine}")

        if device_type() == DeviceName.pi_top_4.value:
            StdoutFormat.print_subsection('EEPROM Configuration')
            eeprom_info = run_command("sudo rpi-eeprom-config", timeout=5)
            print(f"{eeprom_info.strip()}")

    def print_uname_output(self):
        u = uname()
        StdoutFormat.print_line(f"Hostname: {u.nodename}")
        StdoutFormat.print_line(f"Kernel Version: {u.release}")
        StdoutFormat.print_line(f"Kernel Release: {u.version}")

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
        headers_to_skip = ("Build Apt Repo", "Final Apt Repo", "Build Pipeline Commit Hash")
        for k, v in data.items():
            if k in headers_to_skip:
                continue
            StdoutFormat.print_line(f"{k}: {v}")

    def print_debian_version(self):
        debian_version_file = "/etc/debian_version"
        if not path.exists(debian_version_file):
            return
        with open(debian_version_file, 'r') as reader:
            content = reader.read()
        StdoutFormat.print_line(f"Debian Version: {content.strip()}")

    def get_raspi_config_setting_value(self, setting):
        try:
            return run_command(f"raspi-config nonint {setting}", timeout=5).strip()
        except Exception:
            return "Error getting setting"

    def print_raspi_config_settings(self, raspi_config_settings_dict):
        for setting, setting_dict in raspi_config_settings_dict.items():
            setting_value = self.get_raspi_config_setting_value(setting)
            if setting_dict.get("conversion_func"):
                setting_value = setting_dict.get("conversion_func")(setting_value)
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

        StdoutFormat.print_line(f"Hostname: {self.get_raspi_config_setting_value('get_hostname')}")
        StdoutFormat.print_line(f"WiFi Country: {self.get_raspi_config_setting_value('get_wifi_country')}")

        interfaces_list = interfaces()
        # Omit loopback interface
        if "lo" in interfaces_list:
            interfaces_list.remove("lo")
        for iface in interfaces_list:
            StdoutFormat.print_subsection(f"Interface: {iface}")
            print_interface_info(iface)
