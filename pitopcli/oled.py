#!/usr/bin/python3
from time import sleep

from pitop.miniscreen.oled import OLEDDisplay
from .cli_base import CliBaseClass


class OledCLI(CliBaseClass):
    parser_help = "pi-top OLED quick text"
    cli_name = 'oled'

    def __init__(self, request_client, args) -> None:
        self.args = args
        # TODO: add support for 'give/take control to/from hub'
        # REQ_GET_OLED_CONTROL = 125
        # REQ_SET_OLED_CONTROL = 126
        self.request_client = request_client

    def run(self) -> int:
        try:
            oled_screen = OLEDDisplay()
            oled_screen.draw_multiline_text(self.args.text, font_size=self.args.font_size)
            sleep(self.args.timeout)
            return 0
        except Exception:
            return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        parser.add_argument("--timeout", "-t",
                            type=int,
                            help="set the timeout in seconds",
                            default=10,
                            )
        parser.add_argument("--font-size", "-s",
                            type=int,
                            help="set the font size",
                            default=20,
                            )
        parser.add_argument("text",
                            help="set the text to write to screen",
                            )


def main():
    from .deprecated_cli_runner import run
    run(OledCLI)


if __name__ == "__main__":
    main()
