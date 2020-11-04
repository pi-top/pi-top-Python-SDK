#! /usr/bin/python3

import zmq
from subprocess import getstatusoutput
from ptcommon.firmware_device import FirmwareDevice
from ptcommon.command_runner import run_command
from ptcommon.ptdm_message import Message
from ptcommon.common_ids import DeviceID


zmq_socket = None


def main():
    # Get host device and legacy peripheral devices from pt-device-manager
    try:
        connect_to_socket()
        message = get_device_id()
        print_device_id(message)
        for id in range(5):
            message = get_peripheral_enabled(id)
            print_peripheral_enabled(message, id)

    except Exception as e:
        print(f"Unable to get information from pt-device-manager: {str(e)}")

    finally:
        cleanup()

    # Get touchscreen/keyboard from USB devices
    touchscreen_connected = False
    keyboard_connected = False

    resp = run_command("lsusb", timeout=3)
    for line in resp.split("\n"):
        fields = line.split(" ")
        if len(fields) < 6:
            continue
        device_id = fields[5]
        if device_id == "222a:0001":
            touchscreen_connected = True
        elif device_id == "1c4f:0063":
            keyboard_connected = True

        if touchscreen_connected and keyboard_connected:
            break

    print(
        f"pi-top Touchscreen: {'' if touchscreen_connected else 'not '}connected")
    print(f"pi-top Keyboard: {'' if keyboard_connected else 'not '}connected")

    # Firmware-upgradable pi-top peripherals
    if "pi-top [4]" not in run_command("pt-host", timeout=3):
        return

    for device_enum, device_info in FirmwareDevice.device_info.items():
        device_str = device_enum.name

        device_address = device_info.get("i2c_addr")

        if getstatusoutput(f"pt-i2cdetect {device_address}"):
            try:
                fw_device = FirmwareDevice(device_enum)
                human_readable_name = device_str.replace(
                    "_", " ").title().replace("Pt4", "pi-top [4]")
                print(
                    f"Upgradable device connected: {human_readable_name} (v{fw_device.get_fw_version()})")
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


def get_device_id():
    message = Message.from_parts(Message.REQ_GET_DEVICE_ID)
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    return Message.from_string(response_string)


def get_peripheral_enabled(id):
    message = Message.from_parts(Message.REQ_GET_PERIPHERAL_ENABLED, [id])
    zmq_socket.send_string(message.to_string())

    response_string = zmq_socket.recv_string()
    return Message.from_string(response_string)


def print_device_id(message):
    if message.message_id() == Message.RSP_GET_DEVICE_ID:
        if message.validate_parameters([int]):
            device_id = message.parameters()
            if int(device_id[0]) == DeviceID.pi_top.value:
                print("Host device: original pi-top")
            elif int(device_id[0]) == DeviceID.pi_top_ceed.value:
                print("Host device: pi-topCEED")
            elif int(device_id[0]) == DeviceID.pi_top_3.value:
                print("Host device: pi-top [3]")
            elif int(device_id[0]) == DeviceID.pi_top_4.value:
                print("Host device: pi-top [4]")
            else:
                print("Host device: Unknown")
        else:
            print("Error: Unable to get valid device ID.")


def print_peripheral_enabled(message, id):
    p_names = ['pi-topPULSE', 'pi-topSPEAKER-v1-left',
               'pi-topSPEAKER-v1-mono',
               'pi-topSPEAKER-v1-right',  'pi-topSPEAKER-v2']
    if message.message_id() == Message.RSP_GET_PERIPHERAL_ENABLED:
        if message.validate_parameters([int]):
            p_enabled = message.parameters()

            if p_enabled[0] == '1':
                print(f"Connected device: {p_names[id]}")
        else:
            print("Unable to get valid peripheral enabled.")


def cleanup():
    if (zmq_socket is not None):
        zmq_socket.close(0)


if __name__ == "__main__":
    main()
