#!/usr/bin/python3
from time import sleep
from os.path import isfile
from PIL import ImageSequence

from pitopcommon.formatting import is_url

from pitop.miniscreen import OLED
from .cli_base import CliBaseClass


class OledCLI(CliBaseClass):
    parser_help = "pi-top OLED quick text"
    cli_name = 'oled'

    def __init__(self, args) -> None:
        self.args = args
        # TODO: add support for 'give/take control to/from hub'
        # REQ_GET_OLED_CONTROL = 125
        # REQ_SET_OLED_CONTROL = 126

    def run(self) -> int:
        def is_animated(image):
            try:
                image.seek(1)
                return True
            except Exception:
                return False

        try:
            oled = OLED()

            if self.args.force:
                oled.set_control_to_pi()

            if self.args.oled_subcommand == "draw":
                print("Press Ctrl + C to exit.")

                skip_timeout = False
                if isfile(self.args.text) or is_url(self.args.text):
                    oled.set_max_fps(10)
                    img = oled.get_raw_image(self.args.text)
                    skip_timeout = not is_animated(img)

                    for i in range(self.args.loop):
                        for frame in ImageSequence.Iterator(img):
                            oled.draw_image(frame)
                else:
                    oled.draw_multiline_text(self.args.text, font_size=self.args.font_size)

                if skip_timeout:
                    sleep(self.args.timeout)

            else:
                print("Functionality not available yet")

            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="OLED screen utilities",
                                          description="Set of utilities to use pi-top [4]'s OLED screen",
                                          dest="oled_subcommand")

        parser_draw = subparser.add_parser("draw", help="Draw text and images into the OLED")
        parser_draw.add_argument("--force", "-f",
                                 help="Force the hub to give control of the OLED to the Pi",
                                 action="store_true"
                                 )
        parser_draw.add_argument("--timeout", "-t",
                                 type=int,
                                 help="Set the timeout in seconds",
                                 default=10,
                                 )
        parser_draw.add_argument("--font-size", "-s",
                                 type=int,
                                 help="Set the font size",
                                 default=20,
                                 )
        parser_draw.add_argument("--loop", "-l",
                                 type=int,
                                 help="How many times the animated image should be looped",
                                 default=1,
                                 )
        parser_draw.add_argument("text",
                                 help="Set the text to write to screen",
                                 )

        parser_capture = subparser.add_parser("capture", help="Capture images or videos of the OLED content")
        parser_capture.add_argument("--force", "-f",
                                    help="Force the hub to give control of the OLED to the Pi",
                                    action="store_true"
                                    )


def main():
    from .deprecated_cli_runner import run
    run(OledCLI)


if __name__ == "__main__":
    main()
