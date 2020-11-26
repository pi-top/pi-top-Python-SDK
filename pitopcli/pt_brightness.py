#!/usr/bin/env python3

from pitopcommon.ptdm_message import Message
from .pt_cli_base import CliBaseClass


class BrightnessCLI(CliBaseClass):
    parser_help = 'communicate and control the device\'s screen brightness'
    cli_name = "brightness"

    def __init__(self, request_client, args) -> None:
        self.args = args
        self.validate_args()
        self.request_cleint = request_client

    def run(self) -> int:
        try:
            self.send_message_to_device_manager()
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

    def send_message_to_device_manager(self) -> None:
        brightness_val_set = (self.args.brightness_value is not None)
        backlight_state_set = (self.args.backlight is not None)
        timeout_set = (self.args.timeout is not None)

        increment_brightness_set = self.args.increment_brightness
        decrement_brightness_set = self.args.decrement_brightness

        # No parameters - return current brightness
        if not brightness_val_set and not increment_brightness_set and not decrement_brightness_set and not backlight_state_set and not timeout_set:
            self.debug_print("REQ:\tCURRENT BRIGHTNESS", 1)
            resp = self.request_cleint.send_request(Message.REQ_GET_BRIGHTNESS, [])
            if resp.message_id() == Message.RSP_GET_BRIGHTNESS and len(resp.parameters()) > 0:
                print(str(resp.parameters()[0]))
            else:
                raise Exception("Unable to get brightness")

        elif brightness_val_set:
            self.debug_print("REQ:\tSETTING BRIGHTNESS TO " +
                             str(self.args.brightness_value), 1)
            resp = self.request_cleint.send_request(Message.REQ_SET_BRIGHTNESS, parameters=[
                str(self.args.brightness_value)])

        elif increment_brightness_set:
            self.debug_print("REQ:\tINCREMENTING BRIGHTNESS", 1)
            resp = self.request_cleint.send_request(Message.REQ_INCREMENT_BRIGHTNESS)

        elif decrement_brightness_set:
            self.debug_print("REQ:\tDECREMENTING BRIGHTNESS", 1)
            resp = self.request_cleint.send_request(Message.REQ_DECREMENT_BRIGHTNESS)

        elif backlight_state_set:
            if self.args.backlight == 1:
                self.debug_print("REQ:\tTURNING ON BACKLIGHT", 1)
                resp = self.request_cleint.send_request(Message.REQ_UNBLANK_SCREEN)
            else:
                self.debug_print("REQ:\tTURNING OFF BACKLIGHT", 1)
                resp = self.request_cleint.send_request(Message.REQ_BLANK_SCREEN)

        elif timeout_set:
            if self.args.timeout < 0:
                raise Exception("Cannot set timeout < 0")

            if self.args.timeout % 60 != 0:
                raise Exception("Timeout must be a multiple of 60")

            resp = self.request_cleint.send_request(
                Message.REQ_SET_SCREEN_BLANKING_TIMEOUT, [self.args.timeout])

            if resp.message_id() == Message.RSP_SET_SCREEN_BLANKING_TIMEOUT:
                print("OK")
            else:
                print("Setting timeout failed")

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
