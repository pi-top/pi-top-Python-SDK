#! /usr/bin/python3

from pitop.system import (
    device_type,
    legacy_pitop_peripherals,
    upgradable_pitop_peripherals,
    touchscreen_is_connected,
    pitop_keyboard_is_connected
)

from .cli_base import CliBaseClass

from sys import stderr


class DeviceCLI(CliBaseClass):
    parser_help = 'Get information about device and attached pi-top hardware'
    cli_name = 'device'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> None:
        # Get host device and legacy peripheral devices from pt-device-manager
        try:
            device = device_type()
            if device is not None:
                print(f"Host device: {device}")
        except Exception as e:
            print(f"Error on pitop-devices.run: Unable to get device type from pt-device-manager: {e}", file=stderr)

        try:
            for periph in legacy_pitop_peripherals():
                print(f"Connected device: {periph}")
        except Exception as e:
            print(f"Error on pitop-devices.run: Unable to get connected legacy peripherals from pt-device-manager: {e}", file=stderr)

        # Get touchscreen/keyboard from USB devices
        print(f"pi-top Touchscreen: {'' if touchscreen_is_connected() else 'not '}connected")
        print(f"pi-top Keyboard: {'' if pitop_keyboard_is_connected() else 'not '}connected")

        # Firmware-upgradable pi-top peripherals
        if device == "pi-top [4]":
            return

        try:
            for periph in upgradable_pitop_peripherals():
                print(
                    f"Upgradable device connected: {periph.name} (v{periph.fw_version})")
        except Exception as e:
            print(f"Error on pitop-devices.run: Unable to get connected peripherals from pt-device-manager: {e}", file=stderr)

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        pass


def main():
    from .deprecated_cli_runner import run
    run(DeviceCLI)


if __name__ == "__main__":
    main()
