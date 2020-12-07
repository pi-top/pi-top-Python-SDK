#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit

from .brightness import BrightnessCLI
from .devices import DeviceCLI
from .battery import BatteryCLI
from .oled import OledCLI
from .cli_base import PitopCliException


lookup_dict = {
    "brightness": BrightnessCLI,
    "devices": DeviceCLI,
    "battery": BatteryCLI,
    "oled": OledCLI
}


def get_parser():
    """Configures the argument parser according to the CLI classes
    defined in ´lookup_dict´, and returns the parsed arguments.

    Returns:
        Namespace: parsed arguments, as returned by ArgumentParser.parse_args()
    """
    parser = ArgumentParser(prog='pi-top')
    subparsers = parser.add_subparsers(title='Subcommands',
                                       description='Set of valid subcommands to use to interface with your pi-top',
                                       help='valid subcommands',
                                       dest='subcommand')

    for cli_name, cli_class in lookup_dict.items():
        class_parser = subparsers.add_parser(cli_name, help=cli_class.parser_help)
        cli_class.add_parser_arguments(class_parser)

    return parser


def run(args):
    """Executes the command according to the provided arguments"""
    exit_code = 1
    try:
        cls = lookup_dict.get(args.subcommand)
        if cls:
            obj = cls(args)
            exit_code = obj.run()
    except PitopCliException:
        exit_code = 1
    except Exception as e:
        print(f"Error on pitop.run: {e}")
        exit_code = 1

    exit(exit_code)


def main():
    run(get_parser().parse_args())


if __name__ == "__main__":
    main()
