#! /usr/bin/python3

import argparse
from pitop.system import (
    device_info,
    pitop_peripherals,
)

from .cli_base import CliBaseClass

from os import get_terminal_size
from sys import stderr


class StdoutFormat:
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    GREEN = '\033[92m'


class DeviceCLI(CliBaseClass):
    parser_help = 'Get information about device and attached pi-top hardware'
    cli_name = 'devices'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:
        def print_header(section_name):
            print(f"{StdoutFormat.BOLD}{section_name}{StdoutFormat.ENDC} {'='*(get_terminal_size().columns - len(section_name) - 2)}")

        def print_peripheral_line(data):
            if data.get('connected') is False and self.args.quiet:
                return

            if self.args.devices_subcommand is None or not self.args.quiet:
                print(f"[ {StdoutFormat.GREEN}{'✓' if data.get('connected') else ' '}{StdoutFormat.ENDC} ]", end=" ")
            print(f"{data.get('name')}", end=" ")
            if not self.args.name_only and data.get("fw_version"):
                print(f"(v{data.get('fw_version')})", end="")
            print("")

        def print_hub_line(data):
            print(f"{data.get('name')}", end=" ")
            if not self.args.name_only and data.get("fw_version"):
                print(f"(v{data.get('fw_version')})", end="")
            print("")

        # Get host device from device manager
        try:
            device = device_info()
            if self.args.devices_subcommand in ("hub", None):
                if self.args.devices_subcommand is None:
                    print_header("HUB")
                print_hub_line(device)
        except Exception as e:
            print(f"Error on pitop-devices.run: Unable to get device type from pt-device-manager: {e}", file=stderr)
            return 1

        if self.args.devices_subcommand in ("peripherals", None):
            if self.args.devices_subcommand is None:
                print_header("PERIPHERALS")

            try:
                # Get list of all pi-top peripherals
                for periph in pitop_peripherals():
                    print_peripheral_line(periph)
            except Exception as e:
                print(f"Error on pitop-devices.run: Unable to get connected peripherals from pt-device-manager: {e}", file=stderr)
        return 0

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        def add_common_arguments(parser):
            parser.add_argument("--quiet", "-q",
                                help="Display only the connected devices",
                                action="store_true"
                                )
            parser.add_argument("--name-only", "-n",
                                help="Display only the name of the devices, without further information",
                                action="store_true"
                                )

        # to use arguments with "devices" directly
        add_common_arguments(parser)

        # manage arguments common to subparser options (hub & peripherals)
        parent_parser = argparse.ArgumentParser(add_help=False)
        add_common_arguments(parent_parser)

        subparser = parser.add_subparsers(title="pi-top devices utility",
                                          description="Get information about pi-top attached devices",
                                          dest="devices_subcommand")
        # "pitop devices hub" subcommand
        subparser.add_parser("hub", help="Get the name of the active pi-top device", parents=[parent_parser])
        # "pitop devices peripherals" subcommand
        subparser.add_parser("peripherals", help="Get information about attached pi-top peripherals", parents=[parent_parser])


def main():
    from .deprecated_cli_runner import run
    run(DeviceCLI)


def host():
    from .deprecated_cli_runner import run_with_args
    args = {"devices_subcommand": "hub", "name_only": True}
    run_with_args(DeviceCLI,
                  old_command="pt-host",
                  new_command="pi-top devices hub",
                  args_dict=args)


if __name__ == "__main__":
    main()
