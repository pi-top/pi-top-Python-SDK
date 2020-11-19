import zmq

from pitop.utils.ptdm_message import Message


class PTSocket:

    def __init__(self):
        self._zmq_socket = None
        self.connect_to_socket()

    def connect_to_socket(self):
        zmq_context_send = zmq.Context()
        self._zmq_socket = zmq_context_send.socket(zmq.REQ)
        self._zmq_socket.sndtimeo = 1000
        self._zmq_socket.rcvtimeo = 1000
        self._zmq_socket.connect("tcp://127.0.0.1:3782")

    def send_request(self, message_request_id, parameters=list(), verbose=False):
        message = Message.from_parts(message_request_id, parameters)
        self._zmq_socket.send_string(message.to_string())

        response_string = self._zmq_socket.recv_string()
        response_object = Message.from_string(response_string)
        
        if verbose:
            msg = f"RESP:\t{response_object.message_friendly_string()}"
            print(msg)
        return response_object


    def cleanup(self):
        if self._zmq_socket is not None:
            self._zmq_socket.close(0)


