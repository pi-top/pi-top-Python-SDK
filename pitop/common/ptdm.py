from pitop.common.logger import PTLogger
from pitop.common.type_helper import TypeHelper
from threading import Thread
from time import sleep
from inspect import signature
from traceback import format_exc
import zmq
from atexit import (
    register,
    unregister,
)


_TIMEOUT_MS = 1000


# Messages sent to/from pt-device-manager clients
class Message:
    __message_names = dict()
    __param_types = dict()

    # Requests
    REQ_PING = 110
    REQ_GET_DEVICE_ID = 111
    REQ_GET_BRIGHTNESS = 112
    REQ_SET_BRIGHTNESS = 113
    REQ_INCREMENT_BRIGHTNESS = 114
    REQ_DECREMENT_BRIGHTNESS = 115
    REQ_BLANK_SCREEN = 116
    REQ_UNBLANK_SCREEN = 117
    REQ_GET_BATTERY_STATE = 118
    REQ_GET_PERIPHERAL_ENABLED = 119
    REQ_GET_SCREEN_BLANKING_TIMEOUT = 120
    REQ_SET_SCREEN_BLANKING_TIMEOUT = 121
    REQ_GET_LID_OPEN_STATE = 122
    REQ_GET_SCREEN_BACKLIGHT_STATE = 123
    REQ_SET_SCREEN_BACKLIGHT_STATE = 124
    REQ_GET_OLED_CONTROL = 125
    REQ_SET_OLED_CONTROL = 126
    REQ_GET_OLED_SPI_BUS = 127
    REQ_SET_OLED_SPI_BUS = 128

    __message_names[REQ_PING] = "REQ_PING"
    __message_names[REQ_GET_DEVICE_ID] = "REQ_GET_DEVICE_ID"
    __message_names[REQ_GET_BRIGHTNESS] = "REQ_GET_BRIGHTNESS"
    __message_names[REQ_SET_BRIGHTNESS] = "REQ_SET_BRIGHTNESS"
    __message_names[REQ_INCREMENT_BRIGHTNESS] = "REQ_INCREMENT_BRIGHTNESS"
    __message_names[REQ_DECREMENT_BRIGHTNESS] = "REQ_DECREMENT_BRIGHTNESS"
    __message_names[REQ_BLANK_SCREEN] = "REQ_BLANK_SCREEN"
    __message_names[REQ_UNBLANK_SCREEN] = "REQ_UNBLANK_SCREEN"
    __message_names[REQ_GET_BATTERY_STATE] = "REQ_GET_BATTERY_STATE"
    __message_names[REQ_GET_PERIPHERAL_ENABLED] = "REQ_GET_PERIPHERAL_ENABLED"
    __message_names[REQ_GET_SCREEN_BLANKING_TIMEOUT] = "REQ_GET_SCREEN_BLANKING_TIMEOUT"
    __message_names[REQ_SET_SCREEN_BLANKING_TIMEOUT] = "REQ_SET_SCREEN_BLANKING_TIMEOUT"
    __message_names[REQ_GET_LID_OPEN_STATE] = "REQ_GET_LID_OPEN_STATE"
    __message_names[REQ_GET_SCREEN_BACKLIGHT_STATE] = "REQ_GET_SCREEN_BACKLIGHT_STATE"
    __message_names[REQ_SET_SCREEN_BACKLIGHT_STATE] = "REQ_SET_SCREEN_BACKLIGHT_STATE"
    __message_names[REQ_GET_OLED_CONTROL] = "REQ_GET_OLED_CONTROL"
    __message_names[REQ_SET_OLED_CONTROL] = "REQ_SET_OLED_CONTROL"
    __message_names[REQ_GET_OLED_SPI_BUS] = "REQ_GET_OLED_SPI_BUS"
    __message_names[REQ_SET_OLED_SPI_BUS] = "REQ_SET_OLED_SPI_BUS"

    __param_types[REQ_PING] = list()
    __param_types[REQ_GET_DEVICE_ID] = list()
    __param_types[REQ_GET_BRIGHTNESS] = list()
    __param_types[REQ_SET_BRIGHTNESS] = [int]
    __param_types[REQ_INCREMENT_BRIGHTNESS] = list()
    __param_types[REQ_DECREMENT_BRIGHTNESS] = list()
    __param_types[REQ_BLANK_SCREEN] = list()
    __param_types[REQ_UNBLANK_SCREEN] = list()
    __param_types[REQ_GET_BATTERY_STATE] = list()
    __param_types[REQ_GET_PERIPHERAL_ENABLED] = [int]
    __param_types[REQ_GET_SCREEN_BLANKING_TIMEOUT] = list()
    __param_types[REQ_SET_SCREEN_BLANKING_TIMEOUT] = [int]
    __param_types[REQ_GET_LID_OPEN_STATE] = list()
    __param_types[REQ_GET_SCREEN_BACKLIGHT_STATE] = list()
    __param_types[REQ_SET_SCREEN_BACKLIGHT_STATE] = [int]
    __param_types[REQ_GET_OLED_CONTROL] = list()
    __param_types[REQ_SET_OLED_CONTROL] = [int]
    __param_types[REQ_GET_OLED_SPI_BUS] = list()
    __param_types[REQ_SET_OLED_SPI_BUS] = [int]

    # Responses
    RSP_ERR_SERVER = 201
    RSP_ERR_MALFORMED = 202
    RSP_ERR_UNSUPPORTED = 203
    RSP_PING = 210
    RSP_GET_DEVICE_ID = 211
    RSP_GET_BRIGHTNESS = 212
    RSP_SET_BRIGHTNESS = 213
    RSP_INCREMENT_BRIGHTNESS = 214
    RSP_DECREMENT_BRIGHTNESS = 215
    RSP_BLANK_SCREEN = 216
    RSP_UNBLANK_SCREEN = 217
    RSP_GET_BATTERY_STATE = 218
    RSP_GET_PERIPHERAL_ENABLED = 219
    RSP_GET_SCREEN_BLANKING_TIMEOUT = 220
    RSP_SET_SCREEN_BLANKING_TIMEOUT = 221
    RSP_GET_LID_OPEN_STATE = 222
    RSP_GET_SCREEN_BACKLIGHT_STATE = 223
    RSP_SET_SCREEN_BACKLIGHT_STATE = 224
    RSP_GET_OLED_CONTROL = 225
    RSP_SET_OLED_CONTROL = 226
    RSP_GET_OLED_SPI_BUS = 227
    RSP_SET_OLED_SPI_BUS = 228

    __message_names[RSP_ERR_SERVER] = "RSP_ERR_SERVER"
    __message_names[RSP_ERR_MALFORMED] = "RSP_ERR_MALFORMED"
    __message_names[RSP_ERR_UNSUPPORTED] = "RSP_ERR_UNSUPPORTED"
    __message_names[RSP_PING] = "RSP_PING"
    __message_names[RSP_GET_DEVICE_ID] = "RSP_GET_DEVICE_ID"
    __message_names[RSP_GET_BRIGHTNESS] = "RSP_GET_BRIGHTNESS"
    __message_names[RSP_SET_BRIGHTNESS] = "RSP_SET_BRIGHTNESS"
    __message_names[RSP_INCREMENT_BRIGHTNESS] = "RSP_INCREMENT_BRIGHTNESS"
    __message_names[RSP_DECREMENT_BRIGHTNESS] = "RSP_DECREMENT_BRIGHTNESS"
    __message_names[RSP_BLANK_SCREEN] = "RSP_BLANK_SCREEN"
    __message_names[RSP_UNBLANK_SCREEN] = "RSP_UNBLANK_SCREEN"
    __message_names[RSP_GET_BATTERY_STATE] = "RSP_GET_BATTERY_STATE"
    __message_names[RSP_GET_PERIPHERAL_ENABLED] = "RSP_GET_PERIPHERAL_ENABLED"
    __message_names[RSP_GET_SCREEN_BLANKING_TIMEOUT] = "RSP_GET_SCREEN_BLANKING_TIMEOUT"
    __message_names[RSP_SET_SCREEN_BLANKING_TIMEOUT] = "RSP_SET_SCREEN_BLANKING_TIMEOUT"
    __message_names[RSP_GET_LID_OPEN_STATE] = "RSP_GET_LID_OPEN_STATE"
    __message_names[RSP_GET_SCREEN_BACKLIGHT_STATE] = "RSP_GET_SCREEN_BACKLIGHT_STATE"
    __message_names[RSP_SET_SCREEN_BACKLIGHT_STATE] = "RSP_SET_SCREEN_BACKLIGHT_STATE"
    __message_names[RSP_GET_OLED_CONTROL] = "RSP_GET_OLED_CONTROL"
    __message_names[RSP_SET_OLED_CONTROL] = "RSP_SET_OLED_CONTROL"
    __message_names[RSP_GET_OLED_SPI_BUS] = "RSP_GET_OLED_SPI_BUS"
    __message_names[RSP_SET_OLED_SPI_BUS] = "RSP_SET_OLED_SPI_BUS"

    __param_types[RSP_ERR_SERVER] = list()
    __param_types[RSP_ERR_MALFORMED] = list()
    __param_types[RSP_ERR_UNSUPPORTED] = list()
    __param_types[RSP_PING] = list()
    __param_types[RSP_GET_DEVICE_ID] = [int]
    __param_types[RSP_GET_BRIGHTNESS] = [int]
    __param_types[RSP_SET_BRIGHTNESS] = list()
    __param_types[RSP_INCREMENT_BRIGHTNESS] = list()
    __param_types[RSP_DECREMENT_BRIGHTNESS] = list()
    __param_types[RSP_BLANK_SCREEN] = list()
    __param_types[RSP_UNBLANK_SCREEN] = list()
    __param_types[RSP_GET_BATTERY_STATE] = [int, int, int, int]
    __param_types[RSP_GET_PERIPHERAL_ENABLED] = [int]
    __param_types[RSP_GET_SCREEN_BLANKING_TIMEOUT] = [int]
    __param_types[RSP_SET_SCREEN_BLANKING_TIMEOUT] = list()
    __param_types[RSP_GET_LID_OPEN_STATE] = [int]
    __param_types[RSP_GET_SCREEN_BACKLIGHT_STATE] = [int]
    __param_types[RSP_SET_SCREEN_BACKLIGHT_STATE] = list()
    __param_types[RSP_GET_OLED_CONTROL] = [int]
    __param_types[RSP_SET_OLED_CONTROL] = list()
    __param_types[RSP_GET_OLED_SPI_BUS] = [int]
    __param_types[RSP_SET_OLED_SPI_BUS] = list()

    # Broadcast/published messages
    PUB_BRIGHTNESS_CHANGED = 300
    PUB_PERIPHERAL_CONNECTED = 301
    PUB_PERIPHERAL_DISCONNECTED = 302
    PUB_SHUTDOWN_REQUESTED = 303
    PUB_REBOOT_REQUIRED = 304
    PUB_BATTERY_STATE_CHANGED = 305
    PUB_SCREEN_BLANKED = 306
    PUB_SCREEN_UNBLANKED = 307
    PUB_LOW_BATTERY_WARNING = 308
    PUB_CRITICAL_BATTERY_WARNING = 309
    PUB_LID_CLOSED = 310
    PUB_LID_OPENED = 311
    PUB_UNSUPPORTED_HARDWARE = 312
    PUB_V3_BUTTON_UP_PRESSED = 313
    PUB_V3_BUTTON_UP_RELEASED = 314
    PUB_V3_BUTTON_DOWN_PRESSED = 315
    PUB_V3_BUTTON_DOWN_RELEASED = 316
    PUB_V3_BUTTON_SELECT_PRESSED = 317
    PUB_V3_BUTTON_SELECT_RELEASED = 318
    PUB_V3_BUTTON_CANCEL_PRESSED = 319
    PUB_V3_BUTTON_CANCEL_RELEASED = 320
    PUB_KEYBOARD_DOCKED = 321
    PUB_KEYBOARD_UNDOCKED = 322
    PUB_KEYBOARD_CONNECTED = 323
    PUB_FAILED_KEYBOARD_CONNECT = 324
    PUB_OLED_CONTROL_CHANGED = 325
    PUB_OLED_SPI_BUS_CHANGED = 326

    __message_names[PUB_BRIGHTNESS_CHANGED] = "PUB_BRIGHTNESS_CHANGED"
    __message_names[PUB_PERIPHERAL_CONNECTED] = "PUB_PERIPHERAL_CONNECTED"
    __message_names[PUB_PERIPHERAL_DISCONNECTED] = "PUB_PERIPHERAL_DISCONNECTED"
    __message_names[PUB_SHUTDOWN_REQUESTED] = "PUB_SHUTDOWN_REQUESTED"
    __message_names[PUB_REBOOT_REQUIRED] = "PUB_REBOOT_REQUIRED"
    __message_names[PUB_BATTERY_STATE_CHANGED] = "PUB_BATTERY_STATE_CHANGED"
    __message_names[PUB_SCREEN_BLANKED] = "PUB_SCREEN_BLANKED"
    __message_names[PUB_SCREEN_UNBLANKED] = "PUB_SCREEN_UNBLANKED"
    __message_names[PUB_LOW_BATTERY_WARNING] = "PUB_LOW_BATTERY_WARNING"
    __message_names[PUB_CRITICAL_BATTERY_WARNING] = "PUB_CRITICAL_BATTERY_WARNING"
    __message_names[PUB_LID_CLOSED] = "PUB_LID_CLOSED"
    __message_names[PUB_LID_OPENED] = "PUB_LID_OPENED"
    __message_names[PUB_UNSUPPORTED_HARDWARE] = "PUB_UNSUPPORTED_HARDWARE"
    __message_names[PUB_V3_BUTTON_UP_PRESSED] = "PUB_V3_BUTTON_UP_PRESSED"
    __message_names[PUB_V3_BUTTON_UP_RELEASED] = "PUB_V3_BUTTON_UP_RELEASED"
    __message_names[PUB_V3_BUTTON_DOWN_PRESSED] = "PUB_V3_BUTTON_DOWN_PRESSED"
    __message_names[PUB_V3_BUTTON_DOWN_RELEASED] = "PUB_V3_BUTTON_DOWN_RELEASED"
    __message_names[PUB_V3_BUTTON_SELECT_PRESSED] = "PUB_V3_BUTTON_SELECT_PRESSED"
    __message_names[PUB_V3_BUTTON_SELECT_RELEASED] = "PUB_V3_BUTTON_SELECT_RELEASED"
    __message_names[PUB_V3_BUTTON_CANCEL_PRESSED] = "PUB_V3_BUTTON_CANCEL_PRESSED"
    __message_names[PUB_V3_BUTTON_CANCEL_RELEASED] = "PUB_V3_BUTTON_CANCEL_RELEASED"
    __message_names[PUB_KEYBOARD_DOCKED] = "PUB_KEYBOARD_DOCKED"
    __message_names[PUB_KEYBOARD_UNDOCKED] = "PUB_KEYBOARD_UNDOCKED"
    __message_names[PUB_KEYBOARD_CONNECTED] = "PUB_KEYBOARD_CONNECTED"
    __message_names[PUB_FAILED_KEYBOARD_CONNECT] = "PUB_FAILED_KEYBOARD_CONNECT"
    __message_names[PUB_OLED_CONTROL_CHANGED] = "PUB_OLED_CONTROL_CHANGED"
    __message_names[PUB_OLED_SPI_BUS_CHANGED] = "PUB_OLED_SPI_BUS_CHANGED"

    __param_types[PUB_BRIGHTNESS_CHANGED] = [int]
    __param_types[PUB_PERIPHERAL_CONNECTED] = [int]
    __param_types[PUB_PERIPHERAL_DISCONNECTED] = [int]
    __param_types[PUB_SHUTDOWN_REQUESTED] = list()
    __param_types[PUB_REBOOT_REQUIRED] = list()
    __param_types[PUB_BATTERY_STATE_CHANGED] = [int, int, int, int]
    __param_types[PUB_SCREEN_BLANKED] = list()
    __param_types[PUB_SCREEN_UNBLANKED] = list()
    __param_types[PUB_LOW_BATTERY_WARNING] = list()
    __param_types[PUB_CRITICAL_BATTERY_WARNING] = list()
    __param_types[PUB_LID_CLOSED] = list()
    __param_types[PUB_LID_OPENED] = list()
    __param_types[PUB_UNSUPPORTED_HARDWARE] = list()
    __param_types[PUB_V3_BUTTON_UP_PRESSED] = list()
    __param_types[PUB_V3_BUTTON_UP_RELEASED] = list()
    __param_types[PUB_V3_BUTTON_DOWN_PRESSED] = list()
    __param_types[PUB_V3_BUTTON_DOWN_RELEASED] = list()
    __param_types[PUB_V3_BUTTON_SELECT_PRESSED] = list()
    __param_types[PUB_V3_BUTTON_SELECT_RELEASED] = list()
    __param_types[PUB_V3_BUTTON_CANCEL_PRESSED] = list()
    __param_types[PUB_V3_BUTTON_CANCEL_RELEASED] = list()
    __param_types[PUB_KEYBOARD_DOCKED] = list()
    __param_types[PUB_KEYBOARD_UNDOCKED] = list()
    __param_types[PUB_KEYBOARD_CONNECTED] = list()
    __param_types[PUB_FAILED_KEYBOARD_CONNECT] = list()
    __param_types[PUB_OLED_CONTROL_CHANGED] = [int]
    __param_types[PUB_OLED_SPI_BUS_CHANGED] = [int]

    def _parse(self, message_string):
        message_parts = message_string.split("|")

        if len(message_parts) < 1:
            raise ValueError("Message did not have an id")

        if TypeHelper.is_integer(message_parts[0]) is False:
            raise ValueError("Message id was not an integer")

        self._message_id = int(message_parts[0])
        self._parameters = message_parts[1:]

    @classmethod
    def from_string(cls, message_string):
        new_object = cls()
        new_object._parse(message_string)

        new_object.validate_parameters()
        return new_object

    @classmethod
    def from_parts(cls, message_id, parameters=None):
        if parameters is None:
            parameters = list()

        new_object = cls()
        new_object._message_id = message_id
        new_object._parameters = parameters

        new_object.validate_parameters()
        return new_object

    def to_string(self):
        message_to_send = str(self._message_id)

        for message_param in self._parameters:
            message_to_send += "|"
            message_to_send += str(message_param)

        return message_to_send

    def validate_parameters(self):
        expected_param_types = self.__param_types[self._message_id]

        if len(self._parameters) != len(expected_param_types):
            msg = "Message did not have the correct number of parameters"
            msg += " (" + str(len(expected_param_types)) + ")"
            raise ValueError(msg)

        for i in range(len(self._parameters)):
            if expected_param_types[i] == int:
                if TypeHelper.is_integer(self._parameters[i]) is False:
                    msg = "Expected integer parameter could not be parsed"
                    raise ValueError(msg)

            elif expected_param_types[i] == float:
                if TypeHelper.is_float(self._parameters[i]) is False:
                    msg = "Expected float parameter could not be parsed"
                    raise ValueError(msg)

        return True

    @staticmethod
    def name_for_id(message_id):
        return Message.__message_names[message_id]

    def message_id(self):
        return self._message_id

    def message_id_name(self):
        return self.__message_names[self._message_id]

    def message_friendly_string(self):
        result = self.message_id_name()

        for param in self._parameters:
            result += " "
            result += str(param)

        return result

    @property
    def parameters(self):
        return self._parameters


class PTDMRequestClient:
    def __init__(self):
        self.__zmq_context = None
        self.__zmq_socket = None

    def __enter__(self):
        self.__connect_to_socket()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__cleanup()

    def __connect_to_socket(self):
        self.__zmq_context = zmq.Context()
        self.__zmq_socket = self.__zmq_context.socket(zmq.REQ)
        self.__zmq_socket.sndtimeo = _TIMEOUT_MS
        self.__zmq_socket.rcvtimeo = _TIMEOUT_MS

        try:
            self.__zmq_socket.connect("tcp://127.0.0.1:3782")
            PTLogger.debug("pt-device-manager request client is ready")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the request client: " + str(e))
            PTLogger.info(format_exc())
            raise

    def __cleanup(self):
        if self.__zmq_socket is not None:
            self.__zmq_socket.close(linger=0)
            self.__zmq_socket = None

        if self.__zmq_context is not None:
            self.__zmq_context.destroy(linger=0)
            self.__zmq_context = None

    def send_request(self, message_request_id, parameters=list()):
        message = Message.from_parts(message_request_id, parameters)
        self.send_message(message)

    def send_message(self, message):
        initialised = self.__zmq_socket is not None

        # Connect to socket if 'with' syntax was not used
        # This allows for one-off messages to be sent successfully
        if not initialised:
            register(self.__cleanup)
            self.__connect_to_socket()

        # Do exchange
        self.__zmq_socket.send_string(message.to_string())
        response_string = self.__zmq_socket.recv_string()

        # Close socket connection if 'with' syntax was not used
        if not initialised:
            self.__cleanup()
            unregister(self.__cleanup)

        # Parse the response
        response_object = Message.from_string(response_string)

        if response_object.message_id() in [Message.RSP_ERR_SERVER,
                                            Message.RSP_ERR_MALFORMED,
                                            Message.RSP_ERR_UNSUPPORTED]:
            raise Exception(f"pt-device-manager reported an error ({response_object.message_id_name()})")

        # Check response matches initial message (original message value + 100)
        expected_message_id = message.message_id() + 100
        if response_object.message_id() != expected_message_id:
            raise Exception(
                "Invalid response from pt-device-manager. "
                f"Expected: {Message.name_for_id(expected_message_id)}, "
                f"Actual: {response_object.message_id_name()}"
            )

        return response_object


class PTDMSubscribeClient:
    __thread = Thread()

    def __init__(self):
        self.__thread = Thread(target=self.__thread_method)
        self.__thread.setDaemon(True)

        self.__callback_funcs = None

        self.__zmq_context = None
        self.__zmq_socket = None

        self.__continue = False

    def __connect_to_socket(self):
        self.__zmq_context = zmq.Context()
        self.__zmq_socket = self.__zmq_context.socket(zmq.SUB)
        self.__zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        try:
            self.__zmq_socket.connect("tcp://127.0.0.1:3781")
            PTLogger.debug("pt-device-manager subscribe client is ready")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the subscribe client: " + str(e))
            PTLogger.info(format_exc())

            return False

        return True

    def __cleanup(self):
        if self.__zmq_socket is not None:
            self.__zmq_socket.close(linger=0)
            self.__zmq_socket = None

        if self.__zmq_context is not None:
            self.__zmq_context.destroy(linger=0)
            self.__zmq_context = None

    def __thread_method(self):
        poller = zmq.Poller()
        poller.register(self.__zmq_socket, zmq.POLLIN)
        while self.__continue:
            events = poller.poll(_TIMEOUT_MS)

            for i in range(len(events)):
                message_string = self.__zmq_socket.recv_string()
                message = Message.from_string(message_string)

                id = message.message_id()
                if id in self.__callback_funcs:
                    self.invoke_callback_func_if_exists(
                        self.__callback_funcs[id],
                        message.parameters
                    )

    def invoke_callback_func_if_exists(self, func, params=list()):
        if not callable(func):
            return

        func_arg_no = len(signature(func).parameters)
        if func_arg_no > 1:
            raise ValueError("Invalid callback function - it should receive at most one argument.")

        if params == list() or func_arg_no == 0:
            func()
        else:
            func(params)

    def initialise(self, callback_funcs):
        self.__callback_funcs = callback_funcs

    def start_listening(self):
        if not self.__connect_to_socket():
            return False

        # Wait for connection to start
        # TODO: find out if this can be removed
        sleep(0.5)

        self.__continue = True
        self.__thread.start()

        return True

    def stop_listening(self):
        self.__continue = False
        if self.__thread.is_alive():
            self.__thread.join()

        self.__cleanup()
