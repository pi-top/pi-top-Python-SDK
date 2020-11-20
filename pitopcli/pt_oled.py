#!/usr/bin/python3
from pitop.miniscreen.oled import PTOLEDDisplay

from time import sleep
from argparse import ArgumentParser


parser = ArgumentParser(description="pi-top OLED quick text")
parser.add_argument(
    "--timeout",
    type=int,
    help="set the timeout in seconds",
    default=10,
)
parser.add_argument(
    "--font-size",
    type=int,
    help="set the font size",
    default=20,
)

parser.add_argument(
    "text",
    help="set the text to write to screen",
)

args = parser.parse_args()

oled_screen = PTOLEDDisplay()
oled_screen.draw_multiline_text(args.text, font_size=args.font_size)

sleep(args.timeout)
