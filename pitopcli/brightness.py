#!/usr/bin/env python3

from pitop.display import Display
from .cli_base import CliBaseClass


class BrightnessCLI(CliBaseClass):
    parser_help = 'communicate and control the device\'s screen brightness'
    cli_name = "brightness"

    def __init__(self, args) -> None:
        self.args = args
        self.validate_args()

    def run(self) -> int:
        try:
            self.perform_desired_action()
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def debug_print(self, text, required_verbosity_lvl=1) -> None:
        if self.args.verbose is not None and self.args.verbose >= required_verbosity_lvl:
            print(text)

    def validate_args(self) -> None:
        # Handle invalid command line parameter combinations
        if self.args.brightness_value and (self.args.increment_brightness or self.args.decrement_brightness):
            raise Exception("Cannot increment/decrement at the same time as setting brightness value")
        if self.args.increment_brightness and self.args.decrement_brightness:
            raise Exception("Cannot increment and decrement brightness at the same time")

    def perform_desired_action(self) -> None:
        brightness_val_set = (self.args.brightness_value is not None)
        backlight_state_set = (self.args.backlight is not None)
        timeout_set = (self.args.timeout is not None)

        increment_brightness_set = self.args.increment_brightness
        decrement_brightness_set = self.args.decrement_brightness

        display = Display()

        # No parameters - return current brightness
        if not brightness_val_set and not increment_brightness_set and not decrement_brightness_set and not backlight_state_set and not timeout_set:
            self.debug_print("REQ:\tCURRENT BRIGHTNESS", 1)
            print(display.brightness)

        elif brightness_val_set:
            self.debug_print("REQ:\tSETTING BRIGHTNESS TO " +
                             str(self.args.brightness_value), 1)
            display.brightness = self.args.brightness_value

        elif increment_brightness_set:
            self.debug_print("REQ:\tINCREMENTING BRIGHTNESS", 1)
            display.increment_brightness()

        elif decrement_brightness_set:
            self.debug_print("REQ:\tDECREMENTING BRIGHTNESS", 1)
            display.decrement_brightness()

        elif backlight_state_set:
            if self.args.backlight == 1:
                self.debug_print("REQ:\tTURNING ON BACKLIGHT", 1)
                display.backlight = True
            else:
                self.debug_print("REQ:\tTURNING OFF BACKLIGHT", 1)
                display.backlight = False

        elif timeout_set:
            display.blanking_timeout = self.args.timeout

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        parser.add_argument("-b", "--brightness_value",
                            help="Set screen brightness level [1-10] on pi-topHUB, or [1-16] or pi-topHUB v2",
                            type=int,
                            choices=range(1, 17))
        parser.add_argument("-i", "--increment_brightness",
                            help="Increment screen brightness level",
                            action="store_true")
        parser.add_argument("-d", "--decrement_brightness",
                            help="Decrement screen brightness level",
                            action="store_true")
        parser.add_argument("-l", "--backlight",
                            help="Set the screen backlight state [0-1]",
                            type=int,
                            choices=range(2))
        parser.add_argument("-t", "--timeout",
                            help="Set the timeout before the screen blanks in seconds (0 to disable)",
                            type=int)
        parser.add_argument("-v", "--verbose",
                            action="count")


def main():
    from .deprecated_cli_runner import run
    run(BrightnessCLI)


if __name__ == "__main__":
    main()
