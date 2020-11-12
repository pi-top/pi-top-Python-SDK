#!/usr/bin/python3

from sys import stderr
import zmq
from pitop.utils.ptdm_message import Message
from pitop.utils.common_ids import DeviceID


# Error print function
def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


class DeviceTypeClient():

    def __init__(self):
        self.device_id_str = "Unknown"
        self.error_str = None

        self._zmq_socket = None

    def get_host_device(self):
        try:
            self._connect_to_socket()
            message = self._get_device_id()
            self._print_device_id(message)

        except Exception as e:
            self.error_str = f"Unable to get information from pt-device-manager: {str(e)}"

        finally:
            self._cleanup()

    def _connect_to_socket(self):

        zmq_context_send = zmq.Context()
        self._zmq_socket = zmq_context_send.socket(zmq.REQ)
        self._zmq_socket.sndtimeo = 1000
        self._zmq_socket.rcvtimeo = 1000
        self._zmq_socket.connect("tcp://127.0.0.1:3782")

    def send_request(self, message_request_id, parameters):

        message = Message.from_parts(message_request_id, parameters)
        self._zmq_socket.send_string(message.to_string())

        response_string = self._zmq_socket.recv_string()
        return Message.from_string(response_string)

    def _get_device_id(self):

        message = Message.from_parts(Message.REQ_GET_DEVICE_ID)
        self._zmq_socket.send_string(message.to_string())

        response_string = self._zmq_socket.recv_string()
        return Message.from_string(response_string)

    def _print_device_id(self, message):

        if message.message_id() == Message.RSP_GET_DEVICE_ID:
            if message.validate_parameters([int]):
                device_id = message.parameters()
                if int(device_id[0]) == DeviceID.unknown.value:
                    pass

                elif int(device_id[0]) == DeviceID.pi_top.value:
                    self.device_id_str = "Original pi-top"

                elif int(device_id[0]) == DeviceID.pi_top_ceed.value:
                    self.device_id_str = "pi-topCEED"

                elif int(device_id[0]) == DeviceID.pi_top_3.value:
                    self.device_id_str = "pi-top [3]"

                elif int(device_id[0]) == DeviceID.pi_top_4.value:
                    self.device_id_str = "pi-top [4]"

                else:
                    self.error_str = "Unrecognised response from device manager"
            else:
                self.error_str = "Invalid response message parameter(s)"
        else:
            self.error_str = "Invalid response message ID"

    def _cleanup(self):

        if self._zmq_socket is not None:
            self._zmq_socket.close(0)


def main():
    client = DeviceTypeClient()
    client.get_host_device()

    success = client.error_str is None

    if not success:
        eprint(f"Error: {client.error_str}")

    print(client.device_id_str)

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
