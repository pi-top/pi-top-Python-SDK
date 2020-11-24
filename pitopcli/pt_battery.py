#!/usr/bin/env python3

from pitoputils.ptdm_message import Message
from pt_cli_base import CliBaseClass


class BatteryCLI(CliBaseClass):
    parser_help = 'Get battery information from a pi-top.'
    cli_name = "battery"

    def __init__(self, pt_socket, args) -> None:
        self.args = args
        self.socket = pt_socket
        self.args_order = list()

    def run(self) -> int:
        try:
            message = self.socket.send_request(Message.from_parts(Message.REQ_GET_BATTERY_STATE).to_string())
            self.print_battery_state_message(message)
            return 0
        except Exception as e:
            print(f"Error getting battery info: {e}")
            return 1

    def print_battery_state_message(self, message) -> None:
        if self.args.charging_state:
            self.args_order.append('charging-state')
        if self.args.capacity:
            self.args_order.append('capacity')
        if self.args.time_remaining:
            self.args_order.append('time-remaining')
        if self.args.wattage:
            self.args_order.append('wattage')

        if message.message_id() == Message.RSP_GET_BATTERY_STATE:
            if message.validate_parameters([int, int, int, int]):
                charging_state, capacity, time_remaining, wattage = message.parameters()

                if len(self.args_order) > 0:
                    for arg in set(self.args_order):
                        if arg == 'charging-state':
                            print(charging_state)
                        if arg == 'capacity':
                            print(capacity)
                        if arg == 'time-remaining':
                            print(time_remaining)
                        if arg == 'wattage':
                            print(wattage)
                else:

                    if self.args.charging_state:
                        print(charging_state)
                    elif self.args.capacity:
                        print(capacity)
                    elif self.args.time_remaining:
                        print(time_remaining)
                    elif self.args.wattage:
                        print(wattage)
                    else:
                        print("Charging State: " + charging_state)
                        print("Capacity: " + capacity)
                        print("Time Remaining: " + time_remaining)
                        print("Wattage: " + wattage)
            else:
                raise Exception("Unable to get valid battery information.")

    @classmethod
    def add_parser_arguments(cls, parser):
        parser.add_argument("-s", "--charging-state",
                            help="Get charging state. -1 = No pi-top battery detected, 0 = Discharging, 1 = Charging, 2 = Full battery",
                            action="store_true")
        parser.add_argument("-c", "--capacity",
                            help="Get battery capacity percentage (%%)",
                            action="store_true")
        parser.add_argument("-t", "--time-remaining",
                            help="Get the time (in minutes) to full or time to empty based on the charging state",
                            action="store_true")
        parser.add_argument("-w", "--wattage",
                            help="Get the wattage (mAh) of the battery",
                            action="store_true")
        parser.add_argument("-v", "--verbose",
                            action="count")


if __name__ == "__main__":
    from deprecated_cli_runner import run
    run(BatteryCLI)
