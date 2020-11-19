#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit

from pt_socket import PTSocket
from pt_brightness import BrightnessCLI
from pt_device import DeviceCLI
from pt_host import HostCLI
from pt_battery import BatteryCLI
from pt_oled import OledCLI


lookup_dict = {
    "brightness": BrightnessCLI,
    "device": DeviceCLI,
    "host": HostCLI,
    "battery": BatteryCLI,
    "oled": OledCLI
}


def parse_args():
    """Configures the argument parser according to the CLI classes
    defined in ´lookup_dict´, and returns the parsed arguments.

    Returns:
        Namespace: parsed arguments, as returned by ArgumentParser.parse_args()
    """
    parser = ArgumentParser(prog='pt-config')
    subparsers = parser.add_subparsers(title='Subcommands',
                                       description='Set of valid subcommands to use to interface with your pi-top',
                                       help='valid subcommands',
                                       dest='subcommand')
    
    for cli_name, cli_class in lookup_dict.items():
        class_parser = subparsers.add_parser(cli_name, help=cli_class.parser_help)
        cli_class.add_parser_arguments(class_parser)

    return parser.parse_args()


def run(args):
    """Executes the command according to the provided arguments"""
    ptsocket = None
    exit_code = 1
    try:
        ptsocket = PTSocket()
        cls = lookup_dict.get(args.subcommand)
        if cls:
            obj = cls(ptsocket, args)
            exit_code = obj.run()
    except Exception as e:
        print(f"Error: {e}")
        exit_code = 1
    finally:
        if hasattr(ptsocket, "cleanup"):
            ptsocket.cleanup()
    exit(exit_code)


if __name__ == "__main__":
    args = parse_args()
    run(args)
