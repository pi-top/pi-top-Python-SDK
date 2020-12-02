#!/usr/bin/python3
from .cli_base import CliBaseClass
from pitop.miniscreen.oled import set_oled_control_to_pi
from pitop.miniscreen import OLED
from time import sleep


class OledCLI(CliBaseClass):
    parser_help = "pi-top OLED quick text"
    cli_name = 'oled'

    def __init__(self, args) -> None:
        self.args = args
        # TODO: add support for 'give/take control to/from hub'
        # REQ_GET_OLED_CONTROL = 125
        # REQ_SET_OLED_CONTROL = 126

    def run(self) -> int:
        try:
            oled_screen = OLED()
            if self.args.force:
                set_oled_control_to_pi()
            oled_screen.draw_multiline_text(self.args.text, font_size=self.args.font_size)
            sleep(self.args.timeout)
            return 0
        except Exception:
            return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        parser.add_argument("--force", "-f",
                            type=int,
                            help="Force the hub to give control of the OLED to the Pi",
                            default=False,
                            )
        parser.add_argument("--timeout", "-t",
                            type=int,
                            help="Set the timeout in seconds",
                            default=10,
                            )
        parser.add_argument("--font-size", "-s",
                            type=int,
                            help="Set the font size",
                            default=20,
                            )
        parser.add_argument("text",
                            help="Set the text to write to screen",
                            )


def main():
    from .deprecated_cli_runner import run
    run(OledCLI)


if __name__ == "__main__":
    main()
