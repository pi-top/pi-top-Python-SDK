#!/usr/bin/env python3
from argparse import ArgumentParser

from pitop.display import Display
from .cli_base import CliBaseClass, PitopCliException, PitopCliInvalidArgument


class DisplayCLI(CliBaseClass):
    parser_help = "communicate and control the device's display"
    cli_name = "display"

    def __init__(self, args) -> None:
        self.args = args
        self.validate_args()

    def run(self) -> int:
        try:
            self.perform_desired_action()
            return 0
        except Exception as e:
            print(f"Error on pitop-display.run: {e}")
            return 1

    def validate_args(self) -> None:
        if vars(self.args).get('display_subcommand') is None:
            raise PitopCliInvalidArgument
        # Handle invalid command line parameter combinations
        if self.args.display_subcommand != "brightness":
            return
        if self.args.brightness_value and (self.args.increment_brightness or self.args.decrement_brightness):
            print("Error on pitop-display.validate_args: Cannot increment/decrement at the same time as setting brightness value")
            raise PitopCliException
        if self.args.increment_brightness and self.args.decrement_brightness:
            print("Error on pitop-display.validate_args: Cannot increment and decrement brightness at the same time")
            raise PitopCliException

    def perform_desired_action(self) -> None:
        display = Display()

        if self.args.display_subcommand == "brightness":
            if self.args.increment_brightness:
                display.increment_brightness()
            elif self.args.decrement_brightness:
                display.decrement_brightness()
            elif vars(self.args).get("brightness_value") or self.args.brightness_value is not None:
                display.brightness = self.args.brightness_value
            else:
                print(display.brightness)

        elif self.args.display_subcommand == "backlight":
            if vars(self.args).get("backlight_value") is None:
                print(display.backlight)
            else:
                display.backlight = self.args.backlight_value in ("on", 1)

        elif self.args.display_subcommand == "blank_time":
            if vars(self.args).get("timeout_value") is None:
                print(display.blanking_timeout)
            else:
                display.blanking_timeout = self.args.timeout_value

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(title="pi-top display utility",
                                          description="Interface to communicate with the device's display",
                                          dest="display_subcommand")

        # "pi-top display brightness"
        brightness_parser = subparser.add_parser("brightness",
                                                 help="Control display brightness")
        cls.add_brightness_arguments(brightness_parser)

        # "pi-top display backlight"
        backlight_parser = subparser.add_parser("backlight",
                                                help="Control display backlight")
        backlight_parser.add_argument("backlight_value",
                                      help="Set the screen backlight state",
                                      choices=("on", "off", 0, 1),
                                      nargs='?')

        # "pi-top display blank_time"
        timeout_parser = subparser.add_parser("blank_time",
                                              help="Set the time before the screen goes blank on inactivity (0 to disable)")
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
