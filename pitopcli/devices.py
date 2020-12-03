#! /usr/bin/python3

from pitop.system import (
    device_type,
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
            if data.get('connected') is False and vars(self.args).get('quiet'):
                return

            if self.args.devices_subcommand is None or not vars(self.args).get('quiet'):
                print(f"[ {StdoutFormat.GREEN}{'✓' if data.get('connected') else ' '}{StdoutFormat.ENDC} ]", end=" ")
            print(f"{data.get('name')}", end=" ")
            if data.get("fw_version"):
                print(f"(v{data.get('fw_version')})", end="")
            print("")

        # Get host device from device manager
        try:
            device = device_type()
            if self.args.devices_subcommand in ("hub", None):
                if self.args.devices_subcommand is None:
                    print_header("HUB")
                print(f"{device}")
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
        subparser = parser.add_subparsers(title="pi-top devices utility",
                                          description="Get information about pi-top attached devices",
                                          dest="devices_subcommand")

        # "pitop devices hub" subcommand
        subparser.add_parser("hub", help="Get the name of the active pi-top device")
        # "pitop devices peripherals" subcommand
        peripherals_parser = subparser.add_parser("peripherals", help="Get information about attached pi-top peripherals")
        peripherals_parser.add_argument("--quiet", "-q",
                                        help="Display only the connected devices to your pi-top",
                                        action="store_true"
                                        )


def main():
    from .deprecated_cli_runner import run
    run(DeviceCLI)


def host():
    from .deprecated_cli_runner import run_with_args
    args = {"devices_subcommand": "hub"}
    run_with_args(DeviceCLI,
                  old_command="pt-host",
                  new_command="pi-top devices hub",
                  args_dict=args)


if __name__ == "__main__":
    main()
