#!/usr/bin/python3

from os import get_terminal_size

from pitopcommon.command_runner import run_command, run_command_background
from pitopcommon.current_session_info import get_first_display

from .cli_base import CliBaseClass


class StdoutFormat:
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    GREEN = '\033[92m'


class SupportCLI(CliBaseClass):
    parser_help = "Find resources to learn how to use your device and get help if needed."
    cli_name = 'support'

    ONLINE_URI = "https://docs.pi-top.com/python-sdk/"
    LOCAL_URI = "/usr/share/doc/python3-pitop/html/index.html"
    KNOWLEDGE_BASE_URI = "https://knowledgebase.pi-top.com/"
    FORUM_URI = "https://forum.pi-top.com/"

    def __init__(self, args) -> None:
        self.args = args

    def __is_connected_to_internet(self) -> bool:
        try:
            run_command("ping -c1 8.8.8.8", timeout=10, check=True, log_errors=False)
            return True
        except Exception:
            return False

    def __is_doc_package_installed(self):
        try:
            run_command("dpkg -l python3-pitop-doc", timeout=3, check=True, log_errors=False)
            return True
        except Exception:
            return False

    def __get_docs_url(self):
        if self.__is_connected_to_internet():
            return self.ONLINE_URI
        elif self.__is_doc_package_installed():
            return self.LOCAL_URI
        else:
            raise Exception(
                "Not connected to internet and python3-pitop-doc not installed.\n" +
                "Please, connect to the internet or install the documentation package via 'sudo apt install python3-pitop-doc'")

    def run(self) -> int:
        def print_header(section_name):
            print(f"{StdoutFormat.BOLD}{section_name}{StdoutFormat.ENDC} {'='*(get_terminal_size().columns - len(section_name) - 2)}")

        def clickable_text(text, url):
            return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"

        def print_line(title, text, url, status):
            print(f"[ {StdoutFormat.GREEN}{'✓' if status else ' '}{StdoutFormat.ENDC} ]", end=" ")
            print(f"{StdoutFormat.BOLD}{title}{StdoutFormat.ENDC}: {text}\n\t{clickable_text(url, url) if status else url}", end=" ")
            print("")

        def print_docs():
            is_connected = self.__is_connected_to_internet()
            print_header("DOCS")
            print_line("pi-top Python SDK documentation", "online version, recommended", self.ONLINE_URI, is_connected)
            print_line("pi-top Python SDK documentation", "offline version", self.LOCAL_URI, self.__is_doc_package_installed())

        def print_other():
            is_connected = self.__is_connected_to_internet()
            print_header("OTHER")
            print_line("Knowledge Base", "Find answers to commonly asked questions", self.KNOWLEDGE_BASE_URI, is_connected)
            print_line("Forum", "Discuss and search through support topics.", self.FORUM_URI, is_connected)

        if self.args.help_subcommand == "docs":
            if self.args.open:
                display = get_first_display()
                if display is None:
                    raise Exception("There isn't a display available to open the documentation.")
                url = self.__get_docs_url()
                run_command_background(f"x-www-browser {url}")
            elif self.args.preferred:
                print(self.__get_docs_url())
            else:
                print_docs()
        else:
            print_docs()
            print_other()
        return 0

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="pi-top support",
                                          description=cls.parser_help,
                                          dest="help_subcommand")

        docs_parser = subparser.add_parser("docs", help="Find documentation")
        docs_parser.add_argument("--open", "-o",
                                 help="Open a browser with the documentation page",
                                 action="store_true"
                                 )
        docs_parser.add_argument("--preferred", "-p",
                                 help="Print the first available recommended URL to access the documentation",
                                 action="store_true"
                                 )
