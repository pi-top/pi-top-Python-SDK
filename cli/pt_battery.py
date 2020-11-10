#!/usr/bin/env python3

import sys
import zmq
from pitop.utils.ptdm_message import Message
from argparse import ArgumentParser

args = None
args_order = list()
zmq_socket = None


def main():
    error = False
    try:
        parse_args()
        connect_to_socket()
        message = get_battery_state_message()
        print_battery_state_message(message)
        cleanup()

    except Exception as e:
        print_err("Error getting battery info: " + str(e))
        error = True

    finally:
        cleanup()
        sys.exit(1 if error else 0)


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def debug_print(text, required_verbosity_lvl=1):
    try:
        verbose = args.verbose
    except AttributeError:
        verbose = None
    if verbose is not None and verbose >= required_verbosity_lvl:
        print(text)


def parse_args():
    global args

    parser = ArgumentParser(
        description='Get battery information from a pi-top.')
    parser.add_argument("-s", "--charging-state",
                        help="Get charging state. -1 = No pi-top battery detected, 0 = Discharging, 1 = Charging, 2 = Full battery", action="store_true")
    parser.add_argument(
        "-c", "--capacity", help="Get battery capacity percentage (%)", action="store_true")
    parser.add_argument("-t", "--time-remaining",
                        help="Get the time (in minutes) to full or time to empty based on the charging state", action="store_true")
    parser.add_argument(
        "-w", "--wattage", help="Get the wattage (mAh) of the battery", action="store_true")
    parser.add_argument("-v", "--verbose", action="count")

    args = parser.parse_args()

    if len(sys.argv) > 1:

        no_of_args_set = 0
        no_of_args_set = (
            no_of_args_set + 1) if args.charging_state else no_of_args_set
        no_of_args_set = (
            no_of_args_set + 1) if args.capacity else no_of_args_set
        no_of_args_set = (
            no_of_args_set + 1) if args.time_remaining else no_of_args_set
        no_of_args_set = (
            no_of_args_set + 1) if args.wattage else no_of_args_set

        if no_of_args_set > 0:

            for arg in sys.argv[1:]:
                arg_to_parse = arg[1:]
                if arg_to_parse[0] == '-':
                    arg_to_parse = arg_to_parse[1:]
                    if arg_to_parse == 'charging-state' or arg_to_parse == 'capacity' or arg_to_parse == 'time-remaining' or arg_to_parse == 'wattage':
                        args_order.append(arg_to_parse)

                else:
                    for char in arg_to_parse:
                        if char == 's':
                            args_order.append('charging-state')
                        elif char == 'c':
                            args_order.append('capacity')
                        elif char == 't':
                            args_order.append('time-remaining')
                        elif char == 'w':
                            args_order.append('wattage')

    try:
        debug_print("Verbosity level: " + args.verbose)
    except:
        pass


def connect_to_socket():
    global zmq_socket

    zmq_context_send = zmq.Context()
    zmq_socket = zmq_context_send.socket(zmq.REQ)
    zmq_socket.sndtimeo = 1000
    zmq_socket.rcvtimeo = 1000
    zmq_socket.connect("tcp://127.0.0.1:3782")


def send_request(message_request_id, parameters):

    message = Message.from_parts(message_request_id, parameters)
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    return Message.from_string(response_string)


def get_battery_state_message():
    message = Message.from_parts(Message.REQ_GET_BATTERY_STATE)
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    return Message.from_string(response_string)


def print_battery_state_message(message):
    if message.message_id() == Message.RSP_GET_BATTERY_STATE:
        if message.validate_parameters([int, int, int, int]):
            charging_state, capacity, time_remaining, wattage = message.parameters()

            if len(args_order) > 0:

                unique_args_order = list()
                for arg in args_order:
                    if arg not in unique_args_order:
                        unique_args_order.append(arg)

                for arg in unique_args_order:
                    if arg == 'charging-state':
                        print(charging_state)
                    if arg == 'capacity':
                        print(capacity)
                    if arg == 'time-remaining':
                        print(time_remaining)
                    if arg == 'wattage':
                        print(wattage)
            else:
                if args.charging_state:
                    print(charging_state)
                elif args.capacity:
                    print(capacity)
                elif args.time_remaining:
                    print(time_remaining)
                elif args.wattage:
                    print(wattage)
                else:
                    print("Charging State: " + charging_state)
                    print("Capacity: " + capacity)
                    print("Time Remaining: " + time_remaining)
                    print("Wattage: " + wattage)
        else:
            raise Exception("Unable to get valid battery information.")


def cleanup():
    if (zmq_socket is not None):
        zmq_socket.close(0)


if __name__ == "__main__":
    main()
