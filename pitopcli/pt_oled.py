#!/usr/bin/python3
from time import sleep

from pitop.oled import PTOLEDDisplay
from pt_cli_base import CliBaseClass


class OledCLI(CliBaseClass):
    parser_help = "pi-top OLED quick text"
    cli_name = 'oled'

    def __init__(self, pt_socket, args) -> None:
        self.args = args
        self.socket = pt_socket

    def run(self) -> int:
        try:
            oled_screen = PTOLEDDisplay()
            oled_screen.draw_multiline_text(self.args.text, font_size=self.args.font_size)
            sleep(self.args.timeout)
            return 0
        except Exception as e:
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

if __name__ == "__main__":
    from deprecated_cli_runner import run
    run(OledCLI)
