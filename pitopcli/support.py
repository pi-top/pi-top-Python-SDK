#!/usr/bin/python3

from netifaces import (
    AF_LINK,
    AF_INET,
    AF_INET6,
    ifaddresses,
    interfaces,
)
from os import get_terminal_size, uname
from time import asctime, gmtime

from pitopcommon.command_runner import run_command, run_command_background
from pitopcommon.current_session_info import get_first_display

from .cli_base import CliBaseClass


def is_connected_to_internet() -> bool:
    try:
        run_command("ping -c1 8.8.8.8", timeout=10, check=True, log_errors=False)
        return True
    except Exception:
        return False


class StdoutFormat:
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    GREEN = '\033[92m'

    @classmethod
    def print_header(cls, header):
        print(f"{StdoutFormat.BOLD}{header}{StdoutFormat.ENDC} {'='*(get_terminal_size().columns - len(header) - 2)}")

    @classmethod
    def print_section(cls, section):
        print(f"- {StdoutFormat.BOLD}{section}{StdoutFormat.ENDC} {'-'*(get_terminal_size().columns - len(section) - 3)}")

    @classmethod
    def print_line(cls, content):
        print(f"{content}")

    @classmethod
    def clickable_text(cls, text, url):
        return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"

    @classmethod
    def print_checkbox_line(cls, title, text, url, status):
        print(f"[ {StdoutFormat.GREEN}{'✓' if status else ' '}{StdoutFormat.ENDC} ]", end=" ")
        print(f"{StdoutFormat.BOLD}{title}{StdoutFormat.ENDC}: {text}\n\t{cls.clickable_text(url, url) if status else url}", end=" ")
        print("")


class Links:
    ONLINE_URI = "https://docs.pi-top.com/python-sdk/"
    LOCAL_URI = "/usr/share/doc/python3-pitop/html/index.html"
    KNOWLEDGE_BASE_URI = "https://knowledgebase.pi-top.com/"
    FORUM_URI = "https://forum.pi-top.com/"

    def _is_doc_package_installed(self):
        try:
            run_command("dpkg -l python3-pitop-doc", timeout=3, check=True, log_errors=False)
            return True
        except Exception:
            return False

    def get_docs_url(self):
        if is_connected_to_internet():
            return self.ONLINE_URI
        elif self._is_doc_package_installed():
            return self.LOCAL_URI
        else:
            raise Exception(
                "Not connected to internet and python3-pitop-doc not installed.\n" +
                "Please, connect to the internet or install the documentation package via 'sudo apt install python3-pitop-doc'")

    def print_docs(self):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("DOCS")
        StdoutFormat.print_checkbox_line("pi-top Python SDK documentation", "online version, recommended", self.ONLINE_URI, is_connected)
        StdoutFormat.print_checkbox_line("pi-top Python SDK documentation", "offline version", self.LOCAL_URI, self._is_doc_package_installed())

    def print_other(self):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("OTHER")
        StdoutFormat.print_checkbox_line("Knowledge Base", "Find answers to commonly asked questions", self.KNOWLEDGE_BASE_URI, is_connected)
        StdoutFormat.print_checkbox_line("Forum", "Discuss and search through support topics.", self.FORUM_URI, is_connected)

    def open_docs_in_browser(self):
        display = get_first_display()
        if display is None:
            raise Exception("There isn't a display available to open the documentation.")
        url = self.get_docs_url()
        run_command_background(f"x-www-browser {url}")


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

    NETWORK_ENUM_LOOKUP = {AF_LINK: 'LINK_LAYER',
                           AF_INET: 'INTERNET_IPV4',
                           AF_INET6: 'INTERNET_IPV6'}

    def print_os_info(self):
        StdoutFormat.print_section("OS INFORMATION")
        self.print_machine_information()

        StdoutFormat.print_section("raspi-config settings")
        self.print_raspi_config_settings()

        StdoutFormat.print_header("NETWORK SETTINGS")
        self.print_network_settings()

    def print_machine_information(self):
        u = uname()
        print(f"Kernel Name: {u.sysname}")
        print(f"Hostname: {u.nodename}")
        print(f"Kernel Version: {u.release}")
        print(f"Kernel Release: {u.version}")
        print(f"Platform: {u.machine}")

    def print_raspi_config_settings(self):
        def get_setting_value(setting):
            return run_command(f"raspi-config nonint {setting}", timeout=5).strip()

        for setting in self.RASPI_CONFIG_SETTINGS:
            print(f" └ {setting} - {get_setting_value(setting)}")

    def print_network_settings(self):
        def print_interface_info(interface_name):
            iface_info = ifaddresses(interface_name)
            # get network layer, ipv4 and ipv6 info
            for netiface_enum, section_name in self.NETWORK_ENUM_LOOKUP.items():
                interface_info = iface_info.get(netiface_enum)
                if interface_info:
                    for v in interface_info:
                        print(f" └ {section_name} - {v}")

        interfaces_list = interfaces()
        for iface in interfaces_list:
            StdoutFormat.print_section(f"Interface: {iface}")
            print_interface_info(iface)


class SupportCLI(CliBaseClass):
    parser_help = "Find resources to learn how to use your device and get help if needed."
    cli_name = 'support'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:

        if self.args.help_subcommand == "links":
            links = Links()
            if self.args.docs_subcommand == "docs":
                if self.args.open:
                    links.open_docs_in_browser()
                elif self.args.preferred:
                    print(links.get_docs_url())
                else:
                    links.print_docs()
            elif self.args.docs_subcommand == "help":
                links.print_other()
            else:
                links.print_docs()
                links.print_other()
        elif self.args.help_subcommand == "health_check":
            hc = HealthCheck()
            StdoutFormat.print_header("SYSTEM HEALTH CHECK")
            StdoutFormat.print_line(f"Current time (GMT): {asctime(gmtime())}")
            hc.print_os_info()
        return 0

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="pi-top support",
                                          description=cls.parser_help,
                                          dest="help_subcommand")

        # pi-top support links
        links_parser = subparser.add_parser("links", help="Find links to pi-top support pages")

        # pi-top support links docs
        docs_subparser = links_parser.add_subparsers(title="Documentation",
                                                     description="Links to find help and more information about your pi-top",
                                                     dest="docs_subcommand")
        docs_parser = docs_subparser.add_parser("docs", help="pi-top documentation")
        docs_parser.add_argument("--open", "-o",
                                 help="Open a browser with the documentation page",
                                 action="store_true"
                                 )
        docs_parser.add_argument("--preferred", "-p",
                                 help="Print the first available recommended URL to access the documentation",
                                 action="store_true"
                                 )
        # pi-top support links help
        docs_subparser.add_parser("help", help="Places where to look for help")

        # pi-top support health_check
        subparser.add_parser("health_check",
                             help="Perform a system verification to find possible issues")
