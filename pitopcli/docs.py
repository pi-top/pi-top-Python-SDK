#!/usr/bin/python3
from pitopcommon.command_runner import run_command, run_command_background

from .cli_base import CliBaseClass


class DocsCLI(CliBaseClass):
    parser_help = "Easy access to open or find pi-top Python SDK documentation"
    cli_name = 'docs'

    ONLINE_URI = "https://pi-top-pi-top-python-sdk.readthedocs-hosted.com/"
    LOCAL_URI = "file:///usr/share/doc/python3-pitop/html/index.html"

    def __init__(self, args) -> None:
        self.args = args

    def __is_connected_to_internet(self) -> bool:
        try:
            run_command("ping -c1 8.8.8.8", timeout=10, check=True, verbose=False)
            return True
        except Exception:
            return False

    def __get_docs_url(self):
        if self.__is_connected_to_internet():
            return self.ONLINE_URI
        else:
            return self.LOCAL_URI

    def run(self) -> int:
        if self.args.open:
            url = self.__get_docs_url()
            run_command_background(f"x-www-browser {url}")
        elif self.args.quiet:
            print(self.__get_docs_url())
        else:
            print("pi-top Python SDK documentation:")
            print(f" - online version: {self.ONLINE_URI}")
            print(f" - local copy: {self.LOCAL_URI}")
        return 0

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        parser.add_argument("--open", "-o",
                            help="Open a browser with the documentation page",
                            action="store_true"
                            )
        parser.add_argument("--quiet", "-q",
                            help="Print the URL to access the documentation",
                            action="store_true"
                            )
