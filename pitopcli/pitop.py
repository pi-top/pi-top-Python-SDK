#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit

from .battery import BatteryCLI
from .cli_base import PitopCliException, PitopCliInvalidArgument
from .display import DisplayCLI
from .devices import DeviceCLI
from .help import HelpCLI
from .imu import ImuCLI
from .oled import OledCLI


lookup_dict = {
    "battery": BatteryCLI,
    "devices": DeviceCLI,
    "display": DisplayCLI,
    "help": HelpCLI,
    "imu": ImuCLI,
    "oled": OledCLI
}


def get_parser():
    """Configures the argument parser according to the CLI classes
    defined in ´lookup_dict´, and returns the parsed arguments.

    Returns:
        ArgumentParser: parser object
    """
    parser = ArgumentParser(prog='pi-top')
    subparsers = parser.add_subparsers(title='Subcommands',
                                       description='Set of valid subcommands to use to interface with your pi-top',
                                       help='valid subcommands',
                                       dest='subcommand')

    for cli_name, cli_class in lookup_dict.items():
        class_parser = subparsers.add_parser(cli_name, help=cli_class.parser_help)
        cli_class.add_parser_arguments(class_parser)
        cli_class.parser = class_parser

    return parser


def run(args):
    """Executes the command according to the provided arguments"""
    exit_code = 1
    cls = None
    try:
        cls = lookup_dict.get(args.subcommand)
        if cls:
            obj = cls(args)
            exit_code = obj.run()
    except PitopCliException:
        exit_code = 1
    except PitopCliInvalidArgument:
        exit_code = 1
        if cls:
            print(cls.parser.print_help())
    except Exception as e:
        print(f"Error on pitop.run: {e}")
        exit_code = 1

    exit(exit_code)


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        exit(1)
    run(args)


if __name__ == "__main__":
    main()
