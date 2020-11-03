from pitop.core.ptdm_message import Message
from pitop.core.logger import PTLogger
import zmq
import atexit


class RequestClient:
    zmq_socket = None

    def connect_to_socket(self):
        zmq_context_send = zmq.Context()
        self.zmq_socket = zmq_context_send.socket(zmq.REQ)
        self.zmq_socket.sndtimeo = 1000
        self.zmq_socket.rcvtimeo = 1000
        self.zmq_socket.connect("tcp://127.0.0.1:3782")

    def send_message(self, message):
        self.zmq_socket.send_string(message.to_string())
        response_string = self.zmq_socket.recv_string()
        response = Message.from_string(response_string)
        return response

    def init(self):
        atexit.register(self.cleanup)
        self.connect_to_socket()

    def cleanup(self):
        if self.zmq_socket is not None:
            self.zmq_socket.close(0)
        atexit.unregister(self.cleanup)
