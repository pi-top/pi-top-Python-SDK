from pitopcommon.logger import PTLogger
from pitopcommon.ptdm_message import Message
from threading import Thread
from time import sleep
import traceback
import zmq


# Creates a client for publish messages from device manager
# Listens for button presses
class RequestClient:
    _thread = Thread()

    def __init__(self):
        self._thread = Thread(target=self._thread_method)
        self._thread.setDaemon(True)

        self._callback_client = None

        self._zmq_context = zmq.Context()

        self._zmq_socket = self._zmq_context.socket(zmq.SUB)
        self._zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self._continue = False

    def initialise(self, callback_client):
        self._callback_client = callback_client

    def start_listening(self):
        PTLogger.debug("Opening request socket...")

        try:
            self._zmq_socket.connect("tcp://127.0.0.1:3781")
            PTLogger.info("Request client ready.")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the request client: " + str(e))
            PTLogger.info(traceback.format_exc())

            return False

        sleep(0.5)

        self._continue = True
        self._thread.start()

        return True

    def stop_listening(self):
        PTLogger.info("Closing responder socket...")

        self._continue = False
        if self._thread.is_alive():
            self._thread.join()

        self._zmq_socket.close()
        self._zmq_context.destroy()

        PTLogger.debug("Closed responder socket.")

    def _invoke_method_if_exists(self, method):
        if method is not None:
            method()

    def _thread_method(self):
        PTLogger.info("Listening for requests...")

        while self._continue:
            poller = zmq.Poller()
            poller.register(self._zmq_socket, zmq.POLLIN)

            events = poller.poll(500)

            for i in range(len(events)):
                message_string = self._zmq_socket.recv_string()
                message = Message.from_string(message_string)

                if message.message_id() == Message.PUB_V3_BUTTON_UP_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.up.is_pressed = True
                    self._invoke_method_if_exists(
                        self._callback_client.up.when_pressed)

                elif message.message_id() == Message.PUB_V3_BUTTON_DOWN_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.down.is_pressed = True
                    self._invoke_method_if_exists(
                        self._callback_client.down.when_pressed
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_SELECT_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.select.is_pressed = True
                    self._invoke_method_if_exists(
                        self._callback_client.select.when_pressed
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_CANCEL_PRESSED:
                    message.validate_parameters([])
                    self._callback_client.cancel.is_pressed = True
                    self._invoke_method_if_exists(
                        self._callback_client.cancel.when_pressed
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_UP_RELEASED:
                    message.validate_parameters([])
                    self._callback_client.up.is_pressed = False
                    self._invoke_method_if_exists(
                        self._callback_client.up.when_released
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_DOWN_RELEASED:
                    message.validate_parameters([])
                    self._callback_client.down.is_pressed = False
                    self._invoke_method_if_exists(
                        self._callback_client.down.when_released
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_SELECT_RELEASED:
                    message.validate_parameters([])
                    self._callback_client.select.is_pressed = False
                    self._invoke_method_if_exists(
                        self._callback_client.select.when_released
                    )

                elif message.message_id() == Message.PUB_V3_BUTTON_CANCEL_RELEASED:
                    message.validate_parameters([])
                    self._callback_client.cancel.is_pressed = False
                    self._invoke_method_if_exists(
                        self._callback_client.cancel.when_released
                    )
