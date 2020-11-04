#!/usr/bin/env python3

import zmq
from pitop.core.ptdm_message import Message
from argparse import ArgumentParser

args = None
zmq_socket = None


def main():
    try:
        parse_args()
        connect_to_socket()
        send_message_to_device_manager()

    except Exception as e:
        print("Error: " + str(e))

    finally:
        cleanup()


def debug_print(text, required_verbosity_lvl=1):
    try:
        verbose = args.verbose
    except AttributeError:
        verbose = None
    if verbose is not None and verbose >= required_verbosity_lvl:
        print(text)


def parse_args():
    global args

    parser = ArgumentParser()
    parser.add_argument("-b", "--brightness_value",
                        help="Set screen brightness level [1-10] on pi-topHUB, or [1-16] or pi-topHUB v2", type=int, choices=range(1, 17))
    parser.add_argument("-i", "--increment_brightness",
                        help="Increment screen brightness level", action="store_true")
    parser.add_argument("-d", "--decrement_brightness",
                        help="Decrement screen brightness level", action="store_true")
    parser.add_argument(
        "-l", "--backlight", help="Set the screen backlight state [0-1]", type=int, choices=range(2))
    parser.add_argument(
        "-t", "--timeout", help="Set the timeout before the screen blanks in seconds (0 to disable)", type=int)
    parser.add_argument("-v", "--verbose", action="count")

    args = parser.parse_args()

    try:
        print("Verbosity level: " + args.verbose)
    except:
        pass

    # Handle invalid command line parameter combinations
    if args.brightness_value and (args.increment_brightness or args.decrement_brightness):
        raise Exception(
            "Cannot increment/decrement at the same time as setting brightness value")
    if args.increment_brightness and args.decrement_brightness:
        raise Exception(
            "Cannot increment and decrement brightness at the same time")


def connect_to_socket():
    global zmq_socket

    debug_print("Connecting to request server...", 2)
    zmq_context_send = zmq.Context()
    zmq_socket = zmq_context_send.socket(zmq.REQ)
    zmq_socket.sndtimeo = 1000
    zmq_socket.rcvtimeo = 1000
    zmq_socket.connect("tcp://127.0.0.1:3782")
    debug_print("Connected to request server.", 2)


def send_request(message_request_id, parameters=None, required_verbosity_lvl=1):

    message = Message.from_parts(
        message_request_id, parameters if parameters is not None else list())
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    response = Message.from_string(response_string)

    msg = ""
    if required_verbosity_lvl > 0:
        msg += "RESP:\t"
    msg += str(response.message_friendly_string())

    debug_print(msg, required_verbosity_lvl)
    return response


def send_message_to_device_manager():
    brightness_val_set = (args.brightness_value is not None)
    backlight_state_set = (args.backlight is not None)
    timeout_set = (args.timeout is not None)

    increment_brightness_set = args.increment_brightness
    decrement_brightness_set = args.decrement_brightness

    # No parameters - return current brightness
    if not brightness_val_set and not increment_brightness_set and not decrement_brightness_set and not backlight_state_set and not timeout_set:
        debug_print("REQ:\tCURRENT BRIGHTNESS", 1)
        resp = send_request(Message.REQ_GET_BRIGHTNESS,
                            required_verbosity_lvl=1)
        if resp.message_id() == Message.RSP_GET_BRIGHTNESS and len(resp.parameters()) > 0:
            print(str(resp.parameters()[0]))
        else:
            raise Exception("Unable to get brightness")

    elif brightness_val_set:
        debug_print("REQ:\tSETTING BRIGHTNESS TO " +
                    str(args.brightness_value), 1)
        resp = send_request(Message.REQ_SET_BRIGHTNESS, parameters=[
                            str(args.brightness_value)])

    elif increment_brightness_set:
        debug_print("REQ:\tINCREMENTING BRIGHTNESS", 1)
        resp = send_request(Message.REQ_INCREMENT_BRIGHTNESS)

    elif decrement_brightness_set:
        debug_print("REQ:\tDECREMENTING BRIGHTNESS", 1)
        resp = send_request(Message.REQ_DECREMENT_BRIGHTNESS)

    elif backlight_state_set:
        if args.backlight == 1:
            debug_print("REQ:\tTURNING ON BACKLIGHT", 1)
            resp = send_request(Message.REQ_UNBLANK_SCREEN)
        else:
            debug_print("REQ:\tTURNING OFF BACKLIGHT", 1)
            resp = send_request(Message.REQ_BLANK_SCREEN)

    elif timeout_set:
        if args.timeout < 0:
            raise Exception("Cannot set timeout < 0")

        if args.timeout % 60 != 0:
            raise Exception("Timeout must be a multiple of 60")

        resp = send_request(
            Message.REQ_SET_SCREEN_BLANKING_TIMEOUT, [args.timeout])

        if resp.message_id() == Message.RSP_SET_SCREEN_BLANKING_TIMEOUT:
            print("OK")
        else:
            print("Setting timeout failed")


def cleanup():
    debug_print("Closing sockets...", 2)
    if zmq_socket is not None:
        zmq_socket.close(0)

    debug_print("Done.", 2)


if __name__ == "__main__":
    main()
