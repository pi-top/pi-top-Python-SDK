#!/usr/bin/python3

from pitop.system import device_type

from .cli_base import CliBaseClass


class HostCLI(CliBaseClass):
    parser_help = 'Returns the name of the host pi-top device'
    cli_name = 'host'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:
        try:
            device = device_type()
            if device is not None:
                print(device)
                return 0
        except Exception as e:
            print(f"Error: Unable to get information from pt-device-manager: {e}")

        return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        pass


def main():
    from .deprecated_cli_runner import run
    run(HostCLI)


if __name__ == "__main__":
    main()
