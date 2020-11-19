#!/usr/bin/env python3

from argparse import ArgumentParser

from pt_socket import PTSocket
from pt_brightness import BrightnessCLI
from pt_device import DeviceCLI


def parse_args():
    parser = ArgumentParser(prog='pt-config')
    subparsers = parser.add_subparsers(title='Subcommands',
                                       description='Set of valid subcommands to use to interface with your pi-top',
                                       help='valid subcommands',
                                       dest='subcommand')

    parser_brightness = subparsers.add_parser('brightness',
                                              help='communicate and control the device\'s screen brightness')
    parser_brightness.add_argument("-b", "--brightness_value",
                                   help="Set screen brightness level [1-10] on pi-topHUB, or [1-16] or pi-topHUB v2",
                                   type=int,
                                   choices=range(1, 17))
    parser_brightness.add_argument("-i", "--increment_brightness",
                                   help="Increment screen brightness level",
                                   action="store_true")
    parser_brightness.add_argument("-d", "--decrement_brightness",
                                   help="Decrement screen brightness level",
                                   action="store_true")
    parser_brightness.add_argument("-l", "--backlight",
                                   help="Set the screen backlight state [0-1]",
                                   type=int,
                                   choices=range(2))
    parser_brightness.add_argument("-t", "--timeout",
                                   help="Set the timeout before the screen blanks in seconds (0 to disable)",
                                   type=int)
    parser_brightness.add_argument("-v", "--verbose",
                                   action="count")

    device = subparsers.add_parser('device',
                                   help='Get information about device and attached pi-top hardware')

    return parser.parse_args()


def main():
    args = parse_args()
    ptsocket = PTSocket()

    if args.subcommand == "brightness":
        b = BrightnessCLI(ptsocket, args)
        b.run()
    elif args.subcommand == "device":
        b = DeviceCLI(ptsocket, args)
        b.run()

    ptsocket.cleanup()


if __name__ == "__main__":
    main()
