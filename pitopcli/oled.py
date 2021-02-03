#!/usr/bin/python3
from os.path import isfile, isdir, join
from time import sleep, strftime

from pitopcommon.formatting import is_url

from pitop.miniscreen import Miniscreen
from .cli_base import CliBaseClass, PitopCliInvalidArgument


class OledCLI(CliBaseClass):
    parser_help = "pi-top OLED quick text"
    cli_name = 'oled'

    def __init__(self, args) -> None:
        self.args = args
        self.validate_args()

    def validate_args(self) -> None:
        if self.args.oled_subcommand is None:
            raise PitopCliInvalidArgument

    def run(self) -> int:
        def is_animated(image):
            try:
                return image.is_animated
            except AttributeError:
                return False

        def path_to_stored_file(arg_path):
            file_path = ""
            if isfile(arg_path):
                file_path = arg_path
            elif isdir(arg_path):
                file_path = join(arg_path, f"output_{strftime('%Y-%m-%d-%H-%M-%S')}")
            else:
                raise Exception(f"Invalid path: {arg_path}")
            return file_path

        try:
            if self.args.oled_subcommand == "display":
                oled = Miniscreen()

                if self.args.force:
                    oled.set_control_to_pi()

                try:
                    print("Press Ctrl + C to exit.")

                    skip_timeout = False
                    if isfile(self.args.text) or is_url(self.args.text):
                        oled.play_animated_image_file(self.args.text)
                    else:
                        oled.display_multiline_text(self.args.text, font_size=self.args.font_size)

                    if not skip_timeout:
                        sleep(self.args.timeout)

                except KeyboardInterrupt:
                    pass

            elif self.args.oled_subcommand == "spi":
                oled = Miniscreen()

                if self.args.spi_bus is not None:
                    oled.spi_bus = self.args.spi_bus
                else:
                    print(oled.spi_bus)

            elif self.args.oled_subcommand == "capture":
                if self.args.capture_subcommand == "save":
                    file_path = path_to_stored_file(self.args.path)
                    extension = "PNG"
                    print(f"Saving capture to {file_path}.{extension}")
                    oled.canvas.save(f"{file_path}.{extension}")
                elif self.args.capture_subcommand == "start":
                    file_path = path_to_stored_file(self.args.path)
                    print(f"Saving video capture to {self.args.path}")
                elif self.args.capture_subcommand == "stop":
                    print("Stopping video capture")

            return 0
        except Exception as e:
            print(f"Error on pitop-oled.run: {e}")
            return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="OLED screen utilities",
                                          description="Set of utilities to use pi-top [4]'s OLED screen",
                                          dest="oled_subcommand")

        # "capture" arguments
        parser_capture = subparser.add_parser("capture", help="Capture images or videos of the OLED content")
        parser_capture.add_argument("--force", "-f",
                                    help="Force the hub to give control of the OLED to the Pi",
                                    action="store_true"
                                    )
        capture_subparser = parser_capture.add_subparsers(title="Capture images or videos of the OLED content",
                                                          description="description",
                                                          dest="capture_subcommand")
        # "capture save" arguments
        save_parser = capture_subparser.add_parser("save",
                                                   help="Store an image in the given path with the current content of the OLED",
                                                   )
        save_parser.add_argument("--path", "-p",
                                 type=str,
                                 help="Path where snap will be stored. Defaults to /tmp/",
                                 default="/tmp/"
                                 )

        # "capture start" arguments
        start_parser = capture_subparser.add_parser("start",
                                                    help="Start recording OLED screen",
                                                    )
        start_parser.add_argument("--path", "-p",
                                  type=str,
                                  help="Path where video will be stored. Defaults to /tmp/",
                                  default="/tmp/"
                                  )

        capture_subparser.add_parser("stop",
                                     help="Stop recording OLED screen",
                                     )
        # "display" arguments
        parser_display = subparser.add_parser("display", help="Display text and images on the OLED")
        parser_display.add_argument("--force", "-f",
                                    help="Force the hub to give control of the OLED to the Pi",
                                    action="store_true"
                                    )
        parser_display.add_argument("--timeout", "-t",
                                    type=int,
                                    help="Set the timeout in seconds",
                                    default=10,
                                    )
        parser_display.add_argument("--font-size", "-s",
                                    type=int,
                                    help="Set the font size",
                                    default=20,
                                    )
        parser_display.add_argument("--loop", "-l",
                                    type=int,
                                    help="How many times the animated image should be looped",
                                    default=1,
                                    )
        parser_display.add_argument("text",
                                    help="Set the text to write to screen",
                                    )

        # "spi" arguments
        parser_spi = subparser.add_parser("spi", help="Set SPI bus that is used by OLED")
        parser_spi.add_argument("spi_bus",
                                help="SPI bus to be used by OLED. Valid options: {0, 1}",
                                type=int,
                                choices=[0, 1],
                                nargs='?')


def main():
    from .deprecated_cli_runner import run
    run(OledCLI)


if __name__ == "__main__":
    main()
