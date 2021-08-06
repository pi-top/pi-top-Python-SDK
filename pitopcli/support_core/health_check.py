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


from ..formatter import StdoutFormat, StdoutTable
from .ptsoftware import PitopSoftware
from .hub_communication import HubCommunication
from pitop.system import pitop_peripherals

from pitop.system import device_type
from pitop.common.command_runner import run_command
from pitop.common.common_names import DeviceName


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

    VCGENMOD_SETTINGS = {
        "Throttled state of the system": "vcgencmd get_throttled",
        "SoC temperature": "vcgencmd measure_temp",
        "Clock frequency of ARM cores": "vcgencmd measure_clock arm",
        "Clock frequency of VC4 scaler cores": "vcgencmd measure_clock core",
        "Clock frequency of H264 block": "vcgencmd measure_clock H264",
        "Clock frequency of Image Signal Processor": "vcgencmd measure_clock isp",
        "Clock frequency of 3D block": "vcgencmd measure_clock v3d",
        "Clock frequency of UART": "vcgencmd measure_clock uart",
        "Clock frequency of PWM block (analog audio output)": "vcgencmd measure_clock pwm",
        "Clock frequency of SD card interface": "vcgencmd measure_clock emmc",
        "Clock frequency of Pixel valve": "vcgencmd measure_clock pixel",
        "Clock frequency of Analog Video Encoder": "vcgencmd measure_clock vec",
        "Clock frequency of HDMI": "vcgencmd measure_clock hdmi",
        "Clock frequency of Display Peripheral Interface": "vcgencmd measure_clock dpi",
        "Current voltage used by VC4 core": "vcgencmd measure_volts core",
        "Current voltage used by SDRAM core": "vcgencmd measure_volts sdram_c",
        "Current voltage used by SDRAM I/O": "vcgencmd measure_volts sdram_i",
        "Current voltage used by SDRAM Phy": "vcgencmd measure_volts sdram_p",
        "Amount of memory allocated to the ARM cores": "vcgencmd get_mem arm",
        "Amount of memory allocated to VC4": "vcgencmd get_mem gpu",
        "Out Of Memory events occuring in the VC4 memory": "vcgencmd mem_oom",
        "Power status of Main LCD": "vcgencmd display_power -1 0",
        "Power status of Secondary LCD": "vcgencmd display_power -1 1",
        "Power status of HDMI 0": "vcgencmd display_power -1 2",
        "Power status of Composite": "vcgencmd display_power -1 3",
        "Power status of HDMI 1": "vcgencmd display_power -1 7",
        "Resolution & color depth of displays": "vcgencmd get_lcd_info",
    }

    def run(self):
        StdoutFormat.print_header("SYSTEM HEALTH CHECK")
        print(f"Current time: {strftime('%a, %d %b %Y %I:%M:%S %p %Z')}")
        print("")

        self.print_raspberry_pi_device_info()
        print("")

        t = StdoutTable()
        t.add_section("pi-top Devices", self.get_pt_devices_status())
        t.print()

        t = StdoutTable()
        t.add_section("System Information", self.get_system_information())
        t.add_section("Interfaces (via raspi-config)", self.get_raspi_config_settings(self.RASPI_CONFIG_INTERFACES))
        t.add_section("Boot Settings (via raspi-config)", self.get_raspi_config_settings(self.RASPI_CONFIG_BOOT_SETTINGS))
        t.add_section("Misc (via raspi-config)", self.get_raspi_config_settings(self.RASPI_CONFIG_MISC))
        t.print()
        print("")

        StdoutFormat.print_section("Network Settings")
        self.print_network_settings()
        print("")

        StdoutFormat.print_section("pi-top Software Information")
        pt_sw = PitopSoftware()
        StdoutFormat.print_subsection("pi-top Systemd Services")
        pt_sw.print_pt_systemd_status()

        StdoutFormat.print_subsection("pi-top Installed Software")
        StdoutTable().print_data(pt_sw.get_pt_installed_software())

        StdoutFormat.print_subsection("APT Sources")
        pt_sw.print_apt_sources()
        print("")

        StdoutFormat.print_section("pi-top Device Information")
        try:
            hub = HubCommunication()
            hub.print_hub_registers()
        except Exception as e:
            print(f"{e}")

        StdoutFormat.print_subsection("Kernel Diagnostic Messages (dmesg)")
        self.print_dmesg()

    def get_pt_devices_status(self):
        data_arr = []
        for periph in pitop_peripherals():
            connection_status = f"[ {StdoutFormat.GREEN}{'✓' if periph.get('connected') else ' '}{StdoutFormat.ENDC} ]"
            device_name = f"{periph.get('name')}"
            if periph.get("fw_version"):
                device_name += f"(v{periph.get('fw_version')})"
            data_arr.append([connection_status, device_name])
        return data_arr

    def print_dmesg(self):
        try:
            dmesg = run_command("dmesg", timeout=10)
        except Exception:
            dmesg = "Error reading dmesg"

        for line in dmesg.split("\n"):
            StdoutFormat.print_line(line)

    def print_raspberry_pi_device_info(self):
        data_arr = [
            ("Device", f"{run_command('cat /proc/device-tree/model', timeout=2)}"),
            ("Architecture", f"{uname().machine}"),
        ]

        t = StdoutTable()
        t.add_section("Raspberry Pi Device Information", data_arr)
        t.print()

        if device_type() == DeviceName.pi_top_4.value:
            StdoutFormat.print_subsection('Raspberry Pi 4 Bootloader Configuration')
            eeprom_info = run_command("sudo rpi-eeprom-config", timeout=5, check=False)
            print(f"{eeprom_info.strip()}")
            StdoutFormat.print_subsection('Raspberry Pi 4 EEPROM Information')
            eeprom_info = run_command("sudo rpi-eeprom-update", timeout=5, check=False)
            print(f"{eeprom_info.strip()}")
            StdoutFormat.print_subsection('VideoCore GPU Detailed Configuration')
            self.print_vcgenmod_settings()

    def print_vcgenmod_settings(self):
        t = StdoutTable()
        data_arr = []
        for description, command in self.VCGENMOD_SETTINGS.items():
            try:
                result = run_command(command, timeout=1)
                result = result.strip().replace("\n", "; ")
            except Exception:
                result = "Error retrieving information"
            data_arr.append([description, result])
        t.print_data(data_arr)

    def get_uname_output(self):
        data_arr = []
        u = uname()
        data_arr.append(("Kernel Version", u.release))
        data_arr.append(("Kernel Release", u.version))
        return data_arr

    def get_pitopOS_info(self):
        data_arr = []
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
            data_arr.append((k, v))
        return data_arr

    def get_debian_version(self):
        debian_version_file = "/etc/debian_version"
        if not path.exists(debian_version_file):
            return None
        with open(debian_version_file, 'r') as reader:
            content = reader.read()
        return [("Debian Version", content.strip())]

    def get_system_information(self):
        sys_info_arr = self.get_debian_version()
        sys_info_arr += self.get_uname_output()
        sys_info_arr += self.get_pitopOS_info()
        return sys_info_arr

    def get_raspi_config_setting_value(self, setting):
        try:
            return run_command(f"raspi-config nonint {setting}", timeout=5).strip()
        except Exception:
            return "Error getting setting"

    def get_raspi_config_settings(self, raspi_config_settings_dict):
        data_to_print = []

        for setting, setting_dict in raspi_config_settings_dict.items():
            setting_value = self.get_raspi_config_setting_value(setting)
            if setting_dict.get("conversion_func"):
                setting_value = setting_dict.get("conversion_func")(setting_value)
            setting_value = str(setting_value)

            data_to_print.append((setting_dict.get('description'), setting_value))

        return data_to_print

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
                    data_arr = []
                    for addr_attribute, addr_attribute_value in address_info.items():
                        data_arr.append((addr_attribute, addr_attribute_value))

                    t = StdoutTable(indent_level=3 if len(interface_info) > 1 else 2)
                    t.print_data(data_arr)

        t = StdoutTable()
        t.print_data([("Hostname", f"{self.get_raspi_config_setting_value('get_hostname')}"),
                      ("WiFi Country", f"{self.get_raspi_config_setting_value('get_wifi_country')}")])

        interfaces_list = interfaces()
        # Omit loopback interface
        if "lo" in interfaces_list:
            interfaces_list.remove("lo")
        for iface in interfaces_list:
            StdoutFormat.print_subsection(f"Interface: {iface}")
            print_interface_info(iface)
