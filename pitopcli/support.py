#!/usr/bin/python3

from os import get_terminal_size

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
    def print_header(cls, section_name):
        print(f"{StdoutFormat.BOLD}{section_name}{StdoutFormat.ENDC} {'='*(get_terminal_size().columns - len(section_name) - 2)}")

    @classmethod
    def clickable_text(cls, text, url):
        return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"

    @classmethod
    def print_line(cls, title, text, url, status):
        print(f"[ {StdoutFormat.GREEN}{'✓' if status else ' '}{StdoutFormat.ENDC} ]", end=" ")
        print(f"{StdoutFormat.BOLD}{title}{StdoutFormat.ENDC}: {text}\n\t{cls.clickable_text(url, url) if status else url}", end=" ")
        print("")


class Links:
    ONLINE_URI = "https://docs.pi-top.com/python-sdk/"
    LOCAL_URI = "/usr/share/doc/python3-pitop/html/index.html"
    KNOWLEDGE_BASE_URI = "https://knowledgebase.pi-top.com/"
    FORUM_URI = "https://forum.pi-top.com/"

    @classmethod
    def _is_doc_package_installed(cls):
        try:
            run_command("dpkg -l python3-pitop-doc", timeout=3, check=True, log_errors=False)
            return True
        except Exception:
            return False

    @classmethod
    def get_docs_url(cls):
        if is_connected_to_internet():
            return cls.ONLINE_URI
        elif cls._is_doc_package_installed():
            return cls.LOCAL_URI
        else:
            raise Exception(
                "Not connected to internet and python3-pitop-doc not installed.\n" +
                "Please, connect to the internet or install the documentation package via 'sudo apt install python3-pitop-doc'")

    @classmethod
    def print_docs(cls):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("DOCS")
        StdoutFormat.print_line("pi-top Python SDK documentation", "online version, recommended", cls.ONLINE_URI, is_connected)
        StdoutFormat.print_line("pi-top Python SDK documentation", "offline version", cls.LOCAL_URI, cls._is_doc_package_installed())

    @classmethod
    def print_other(cls):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("OTHER")
        StdoutFormat.print_line("Knowledge Base", "Find answers to commonly asked questions", cls.KNOWLEDGE_BASE_URI, is_connected)
        StdoutFormat.print_line("Forum", "Discuss and search through support topics.", cls.FORUM_URI, is_connected)

    @classmethod
    def open_docs_in_browser(cls):
        display = get_first_display()
        if display is None:
            raise Exception("There isn't a display available to open the documentation.")
        url = cls.get_docs_url()
        run_command_background(f"x-www-browser {url}")


class SupportCLI(CliBaseClass):
    parser_help = "Find resources to learn how to use your device and get help if needed."
    cli_name = 'support'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:

        if self.args.help_subcommand == "links":
            if self.args.docs_subcommand == "docs":
                if self.args.open:
                    Links.open_docs_in_browser()
                elif self.args.preferred:
                    print(Links.get_docs_url())
                else:
                    Links.print_docs()
            elif self.args.docs_subcommand == "help":
                Links.print_other()
            else:
                Links.print_docs()
                Links.print_other()
        elif self.args.help_subcommand == "health_check":
            pass
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
        subparser.add_parser("System Health Check",
                             help="Perform a system verification to find possible issues")
