#!/usr/bin/env python3
from argparse import ArgumentParser

from pitop.display import Display
from .cli_base import CliBaseClass, PitopCliException


class DisplayCLI(CliBaseClass):
    parser_help = 'communicate and control the device\'s display'
    cli_name = "display"

    def __init__(self, args) -> None:
        self.args = args
        self.validate_args()

    def run(self) -> int:
        try:
            self.perform_desired_action()
            return 0
        except Exception as e:
            print(f"Error on pitop-brightness.run: {e}")
            return 1

    def debug_print(self, text, required_verbosity_lvl=1) -> None:
        if self.args.verbose is not None and self.args.verbose >= required_verbosity_lvl:
            print(text)

    def validate_args(self) -> None:
        # Handle invalid command line parameter combinations
        if self.args.display_subcommand != "brightness":
            return
        if self.args.brightness_value and (self.args.increment_brightness or self.args.decrement_brightness):
            print("Error on pitop-brightness.validate_args: Cannot increment/decrement at the same time as setting brightness value")
            raise PitopCliException
        if self.args.increment_brightness and self.args.decrement_brightness:
            print("Error on pitop-brightness.validate_args: Cannot increment and decrement brightness at the same time")
            raise PitopCliException

    def perform_desired_action(self) -> None:
        display = Display()

        if self.args.display_subcommand == "brightness":
            if self.args.increment_brightness:
                self.debug_print("REQ:\tINCREMENTING BRIGHTNESS", 1)
                display.increment_brightness()
            elif self.args.decrement_brightness:
                self.debug_print("REQ:\tDECREMENTING BRIGHTNESS", 1)
                display.decrement_brightness()
            elif vars(self.args).get('brightness_value') or self.args.brightness_value is not None:
                self.debug_print("REQ:\tSETTING BRIGHTNESS TO " +
                                 str(self.args.brightness_value), 1)
                display.brightness = self.args.brightness_value
            else:
                self.debug_print("REQ:\tCURRENT BRIGHTNESS", 1)
                print(display.brightness)

        elif self.args.display_subcommand == "backlight":
            if vars(self.args).get('backlight_value') is None:
                self.debug_print("REQ:\tCURRENT BACKLIGHT", 1)
                print(display.backlight)
            else:
                backlight_state = self.args.backlight_value > 0
                self.debug_print(f"REQ:\tTURNING {'ON' if backlight_state else 'OFF'} BACKLIGHT", 1)
                display.backlight = backlight_state

        elif self.args.display_subcommand == "timeout":
            if vars(self.args).get('timeout_value') is None:
                self.debug_print("REQ:\tCURRENT TIMEOUT", 1)
                print(display.blanking_timeout)
            else:
                self.debug_print(f"REQ:\tSETTING TIMEOUT TO {self.args.timeout_value}", 1)
                display.blanking_timeout = self.args.timeout_value

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="pi-top display utility",
                                          description="Interface to communicate with the device\'s display",
                                          required=True,
                                          dest="display_subcommand")

        # manage arguments common to subparser options
        parent_parser = ArgumentParser(add_help=False)
        parent_parser.add_argument("-v", "--verbose",
                                   action="count")

        # "pi-top display brightness"
        brightness_parser = subparser.add_parser("brightness", help="Control display brightness", parents=[parent_parser])
        cls.add_brightness_arguments(brightness_parser)

        # "pi-top display backlight"
        backlight_parser = subparser.add_parser("backlight", help="Control display backlight", parents=[parent_parser])
        backlight_parser.add_argument("backlight_value",
                                      help="Set the screen backlight state [0-1]",
                                      type=int,
                                      choices=range(2),
                                      nargs='?')

        # "pi-top display timeout"
        timeout_parser = subparser.add_parser(
            "timeout", help="Set the timeout before the screen blanks in seconds (0 to disable)", parents=[parent_parser])
        timeout_parser.add_argument("timeout_value",
                                    help="Timeout value",
                                    type=int,
                                    nargs='?')

    @classmethod
    def add_brightness_arguments(cls, parser):
        parser.add_argument("brightness_value",
                            help="Set screen brightness level [1-10] on pi-topHUB, or [1-16] or pi-topHUB v2",
                            type=int,
                            choices=range(1, 17),
                            nargs='?')
        parser.add_argument("-i", "--increment_brightness",
                            help="Increment screen brightness level",
                            action="store_true")
        parser.add_argument("-d", "--decrement_brightness",
                            help="Decrement screen brightness level",
                            action="store_true")


def main():
    from .deprecated_cli_runner import run
    run(DisplayCLI)


def brightness():
    parser = ArgumentParser("brightness", description="Control display brightness")
    DisplayCLI.add_brightness_arguments(parser)
    args = parser.parse_args()
    args = vars(args)
    args["display_subcommand"] = "brightness"

    from .deprecated_cli_runner import run_with_args
    run_with_args(DisplayCLI,
                  old_command="pt-brightness",
                  new_command="pi-top display brightness",
                  args_dict=args)


if __name__ == "__main__":
    main()
