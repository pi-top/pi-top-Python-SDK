#!/usr/bin/python3
from time import sleep

from pitop.oled import PTOLEDDisplay


class OledCLI:
    def __init__(self, pt_socket, args):
        self.args = args
        self.socket = pt_socket

    def run(self):
        oled_screen = PTOLEDDisplay()
        oled_screen.draw_multiline_text(self.args.text, font_size=self.args.font_size)
        sleep(self.args.timeout)
