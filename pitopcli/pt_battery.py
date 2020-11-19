#!/usr/bin/env python3

from pitop.utils.ptdm_message import Message


class BatteryCLI():

    def __init__(self, pt_socket, args):
        self.args = args
        self.socket = pt_socket
        self.args_order = list()

    def run(self):
        error = False
        try:
            message = self.socket.send_request(Message.from_parts(Message.REQ_GET_BATTERY_STATE).to_string())
            self.print_battery_state_message(message)
        except Exception as e:
            print(f"Error getting battery info: {e}")

    def print_battery_state_message(self, message):
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
