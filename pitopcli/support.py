#!/usr/bin/python3
from .cli_base import CliBaseClass
from .support_core import HealthCheck, Links


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
            hc.run()
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
