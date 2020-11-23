#!/usr/bin/python3

from pitop.utils.ptdm_message import Message
from pitop.utils.common_ids import DeviceID

from pt_cli_base import CliBaseClass


class HostCLI(CliBaseClass):
    parser_help = 'Returns the name of the host pi-top device'
    cli_name = 'host'

    def __init__(self, pt_socket, args) -> None:
        self.args = args
        self.socket = pt_socket

    def run(self) -> int:
        try:
            message = self.socket.send_request(Message.from_parts(Message.REQ_GET_DEVICE_ID).to_string())
            status = self.print_device_id(message)
            return status
        except Exception as e:
            print(f"Error: Unable to get information from pt-device-manager: {e}")
            return 1

    def print_device_id(self, message) -> int:
        device_lookup = {
            DeviceID.unknown.value:  "Unknown",
            DeviceID.pi_top.value: "Original pi-top",
            DeviceID.pi_top_ceed.value: "pi-topCEED",
            DeviceID.pi_top_3.value: "pi-top [3]",
            DeviceID.pi_top_4.value: "pi-top [4]",
        }

        if message.message_id() == Message.RSP_GET_DEVICE_ID:
            if message.validate_parameters([int]):
                device_id = message.parameters()
                device_str = device_lookup.get(int(device_id[0]))
                if device_str:
                    print(device_str)
                    return 0
                else:
                    print("Unrecognised response from device manager")
            else:
                print("Invalid response message parameter(s)")
        else:
            print("Invalid response message ID")
        return 1

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        pass


if __name__ == "__main__":
    from deprecated_cli_runner import run
    run(HostCLI)
