#!/usr/bin/env python3

from pitop.utils.ptdm_message import Message


class BrightnessCLI:
    def __init__(self, pt_socket, args) -> None:
        self.args = args
        self.validate_args()
        self.socket = pt_socket

    def run(self):
        try:
            self.send_message_to_device_manager()
        except Exception as e:
            print(f"Error: {e}")

    def debug_print(self, text, required_verbosity_lvl=1):
        if self.args.verbose is not None and self.args.verbose >= required_verbosity_lvl:
            print(text)

    def validate_args(self):
        # Handle invalid command line parameter combinations
        if self.args.brightness_value and (self.args.increment_brightness or self.args.decrement_brightness):
            raise Exception("Cannot increment/decrement at the same time as setting brightness value")
        if self.args.increment_brightness and self.args.decrement_brightness:
            raise Exception("Cannot increment and decrement brightness at the same time")

    def send_message_to_device_manager(self):
        brightness_val_set = (self.args.brightness_value is not None)
        backlight_state_set = (self.args.backlight is not None)
        timeout_set = (self.args.timeout is not None)

        increment_brightness_set = self.args.increment_brightness
        decrement_brightness_set = self.args.decrement_brightness

        # No parameters - return current brightness
        if not brightness_val_set and not increment_brightness_set and not decrement_brightness_set and not backlight_state_set and not timeout_set:
            self.debug_print("REQ:\tCURRENT BRIGHTNESS", 1)
            resp = self.socket.send_request(Message.REQ_GET_BRIGHTNESS, [])
            if resp.message_id() == Message.RSP_GET_BRIGHTNESS and len(resp.parameters()) > 0:
                print(str(resp.parameters()[0]))
            else:
                raise Exception("Unable to get brightness")

        elif brightness_val_set:
            self.debug_print("REQ:\tSETTING BRIGHTNESS TO " +
                             str(self.args.brightness_value), 1)
            resp = self.socket.send_request(Message.REQ_SET_BRIGHTNESS, parameters=[
                str(self.args.brightness_value)])

        elif increment_brightness_set:
            self.debug_print("REQ:\tINCREMENTING BRIGHTNESS", 1)
            resp = self.socket.send_request(Message.REQ_INCREMENT_BRIGHTNESS)

        elif decrement_brightness_set:
            self.debug_print("REQ:\tDECREMENTING BRIGHTNESS", 1)
            resp = self.socket.send_request(Message.REQ_DECREMENT_BRIGHTNESS)

        elif backlight_state_set:
            if self.args.backlight == 1:
                self.debug_print("REQ:\tTURNING ON BACKLIGHT", 1)
                resp = self.socket.send_request(Message.REQ_UNBLANK_SCREEN)
            else:
                self.debug_print("REQ:\tTURNING OFF BACKLIGHT", 1)
                resp = self.socket.send_request(Message.REQ_BLANK_SCREEN)

        elif timeout_set:
            if self.args.timeout < 0:
                raise Exception("Cannot set timeout < 0")

            if self.args.timeout % 60 != 0:
                raise Exception("Timeout must be a multiple of 60")

            resp = self.socket.send_request(
                Message.REQ_SET_SCREEN_BLANKING_TIMEOUT, [self.args.timeout])

            if resp.message_id() == Message.RSP_SET_SCREEN_BLANKING_TIMEOUT:
                print("OK")
            else:
                print("Setting timeout failed")
