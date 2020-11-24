# Messages sent to/from pt-device-manager clients
class TypeHelper:
    @staticmethod
    def _is_integer(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False


class Message:
    _message_names = dict()

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

    _message_names[REQ_PING] = "REQ_PING"
    _message_names[REQ_GET_DEVICE_ID] = "REQ_GET_DEVICE_ID"
    _message_names[REQ_GET_BRIGHTNESS] = "REQ_GET_BRIGHTNESS"
    _message_names[REQ_SET_BRIGHTNESS] = "REQ_SET_BRIGHTNESS"
    _message_names[REQ_INCREMENT_BRIGHTNESS] = "REQ_INCREMENT_BRIGHTNESS"
    _message_names[REQ_DECREMENT_BRIGHTNESS] = "REQ_DECREMENT_BRIGHTNESS"
    _message_names[REQ_BLANK_SCREEN] = "REQ_BLANK_SCREEN"
    _message_names[REQ_UNBLANK_SCREEN] = "REQ_UNBLANK_SCREEN"
    _message_names[REQ_GET_BATTERY_STATE] = "REQ_GET_BATTERY_STATE"
    _message_names[REQ_GET_PERIPHERAL_ENABLED] = "REQ_GET_PERIPHERAL_ENABLED"
    _message_names[REQ_GET_SCREEN_BLANKING_TIMEOUT] = "REQ_GET_SCREEN_BLANKING_TIMEOUT"
    _message_names[REQ_SET_SCREEN_BLANKING_TIMEOUT] = "REQ_SET_SCREEN_BLANKING_TIMEOUT"
    _message_names[REQ_GET_LID_OPEN_STATE] = "REQ_GET_LID_OPEN_STATE"
    _message_names[REQ_GET_SCREEN_BACKLIGHT_STATE] = "REQ_GET_SCREEN_BACKLIGHT_STATE"
    _message_names[REQ_SET_SCREEN_BACKLIGHT_STATE] = "REQ_SET_SCREEN_BACKLIGHT_STATE"
    _message_names[REQ_GET_OLED_CONTROL] = "REQ_GET_OLED_CONTROL"
    _message_names[REQ_SET_OLED_CONTROL] = "REQ_SET_OLED_CONTROL"

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
    RSP_BLANK_SCREEN = 116
    RSP_UNBLANK_SCREEN = 117
    RSP_GET_BATTERY_STATE = 218
    RSP_GET_PERIPHERAL_ENABLED = 219
    RSP_GET_SCREEN_BLANKING_TIMEOUT = 220
    RSP_SET_SCREEN_BLANKING_TIMEOUT = 221
    RSP_GET_LID_OPEN_STATE = 222
    RSP_GET_SCREEN_BACKLIGHT_STATE = 223
    RSP_SET_SCREEN_BACKLIGHT_STATE = 224
    RSP_GET_OLED_CONTROL = 225
    RSP_SET_OLED_CONTROL = 226

    _message_names[RSP_ERR_SERVER] = "RSP_ERR_SERVER"
    _message_names[RSP_ERR_MALFORMED] = "RSP_ERR_MALFORMED"
    _message_names[RSP_ERR_UNSUPPORTED] = "RSP_ERR_UNSUPPORTED"
    _message_names[RSP_PING] = "RSP_PING"
    _message_names[RSP_GET_DEVICE_ID] = "RSP_GET_DEVICE_ID"
    _message_names[RSP_GET_BRIGHTNESS] = "RSP_GET_BRIGHTNESS"
    _message_names[RSP_SET_BRIGHTNESS] = "RSP_SET_BRIGHTNESS"
    _message_names[RSP_INCREMENT_BRIGHTNESS] = "RSP_INCREMENT_BRIGHTNESS"
    _message_names[RSP_DECREMENT_BRIGHTNESS] = "RSP_DECREMENT_BRIGHTNESS"
    _message_names[RSP_BLANK_SCREEN] = "RSP_BLANK_SCREEN"
    _message_names[RSP_UNBLANK_SCREEN] = "RSP_UNBLANK_SCREEN"
    _message_names[RSP_GET_BATTERY_STATE] = "RSP_GET_BATTERY_STATE"
    _message_names[RSP_GET_PERIPHERAL_ENABLED] = "RSP_GET_PERIPHERAL_ENABLED"
    _message_names[RSP_GET_SCREEN_BLANKING_TIMEOUT] = "RSP_GET_SCREEN_BLANKING_TIMEOUT"
    _message_names[RSP_SET_SCREEN_BLANKING_TIMEOUT] = "RSP_SET_SCREEN_BLANKING_TIMEOUT"
    _message_names[RSP_GET_LID_OPEN_STATE] = "RSP_GET_LID_OPEN_STATE"
    _message_names[RSP_GET_SCREEN_BACKLIGHT_STATE] = "RSP_GET_SCREEN_BACKLIGHT_STATE"
    _message_names[RSP_SET_SCREEN_BACKLIGHT_STATE] = "RSP_SET_SCREEN_BACKLIGHT_STATE"
    _message_names[RSP_GET_OLED_CONTROL] = "RSP_GET_OLED_CONTROL"
    _message_names[RSP_SET_OLED_CONTROL] = "RSP_SET_OLED_CONTROL"

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
    PUB_NATIVE_DISPLAY_CONNECTED = 326
    PUB_NATIVE_DISPLAY_DISCONNECTED = 327
    PUB_EXTERNAL_DISPLAY_CONNECTED = 328
    PUB_EXTERNAL_DISPLAY_DISCONNECTED = 329

    _message_names[PUB_BRIGHTNESS_CHANGED] = "PUB_BRIGHTNESS_CHANGED"
    _message_names[PUB_PERIPHERAL_CONNECTED] = "PUB_PERIPHERAL_CONNECTED"
    _message_names[PUB_PERIPHERAL_DISCONNECTED] = "PUB_PERIPHERAL_DISCONNECTED"
    _message_names[PUB_SHUTDOWN_REQUESTED] = "PUB_SHUTDOWN_REQUESTED"
    _message_names[PUB_REBOOT_REQUIRED] = "PUB_REBOOT_REQUIRED"
    _message_names[PUB_BATTERY_STATE_CHANGED] = "PUB_BATTERY_STATE_CHANGED"
    _message_names[PUB_SCREEN_BLANKED] = "PUB_SCREEN_BLANKED"
    _message_names[PUB_SCREEN_UNBLANKED] = "PUB_SCREEN_UNBLANKED"
    _message_names[PUB_LOW_BATTERY_WARNING] = "PUB_LOW_BATTERY_WARNING"
    _message_names[PUB_CRITICAL_BATTERY_WARNING] = "PUB_CRITICAL_BATTERY_WARNING"
    _message_names[PUB_LID_CLOSED] = "PUB_LID_CLOSED"
    _message_names[PUB_LID_OPENED] = "PUB_LID_OPENED"
    _message_names[PUB_UNSUPPORTED_HARDWARE] = "PUB_UNSUPPORTED_HARDWARE"
    _message_names[PUB_V3_BUTTON_UP_PRESSED] = "PUB_V3_BUTTON_UP_PRESSED"
    _message_names[PUB_V3_BUTTON_UP_RELEASED] = "PUB_V3_BUTTON_UP_RELEASED"
    _message_names[PUB_V3_BUTTON_DOWN_PRESSED] = "PUB_V3_BUTTON_DOWN_PRESSED"
    _message_names[PUB_V3_BUTTON_DOWN_RELEASED] = "PUB_V3_BUTTON_DOWN_RELEASED"
    _message_names[PUB_V3_BUTTON_SELECT_PRESSED] = "PUB_V3_BUTTON_SELECT_PRESSED"
    _message_names[PUB_V3_BUTTON_SELECT_RELEASED] = "PUB_V3_BUTTON_SELECT_RELEASED"
    _message_names[PUB_V3_BUTTON_CANCEL_PRESSED] = "PUB_V3_BUTTON_CANCEL_PRESSED"
    _message_names[PUB_V3_BUTTON_CANCEL_RELEASED] = "PUB_V3_BUTTON_CANCEL_RELEASED"
    _message_names[PUB_KEYBOARD_DOCKED] = "PUB_KEYBOARD_DOCKED"
    _message_names[PUB_KEYBOARD_UNDOCKED] = "PUB_KEYBOARD_UNDOCKED"
    _message_names[PUB_KEYBOARD_CONNECTED] = "PUB_KEYBOARD_CONNECTED"
    _message_names[PUB_FAILED_KEYBOARD_CONNECT] = "PUB_FAILED_KEYBOARD_CONNECT"
    _message_names[PUB_OLED_CONTROL_CHANGED] = "PUB_OLED_CONTROL_CHANGED"
    _message_names[PUB_NATIVE_DISPLAY_CONNECTED] = "PUB_NATIVE_DISPLAY_CONNECTED"
    _message_names[PUB_NATIVE_DISPLAY_DISCONNECTED] = "PUB_NATIVE_DISPLAY_DISCONNECTED"
    _message_names[PUB_EXTERNAL_DISPLAY_CONNECTED] = "PUB_EXTERNAL_DISPLAY_CONNECTED"
    _message_names[PUB_EXTERNAL_DISPLAY_DISCONNECTED] = "PUB_EXTERNAL_DISPLAY_DISCONNECTED"

    def _parse(self, message_string):
        message_parts = message_string.split("|")

        if len(message_parts) < 1:
            raise ValueError("Message did not have an id")

        if TypeHelper._is_integer(message_parts[0]) is False:
            raise ValueError("Message id was not an integer")

        self._message_id = int(message_parts[0])
        self._parameters = message_parts[1:]

    @classmethod
    def from_string(cls, message_string):
        new_object = cls()
        new_object._parse(message_string)

        return new_object

    @classmethod
    def from_parts(cls, message_id, parameters=None):
        if parameters is None:
            parameters = list()

        new_object = cls()
        new_object._message_id = message_id
        new_object._parameters = parameters

        return new_object

    def to_string(self):
        message_to_send = str(self._message_id)

        for message_param in self._parameters:
            message_to_send += "|"
            message_to_send += str(message_param)

        return message_to_send

    def validate_parameters(self, expected_param_types):
        if len(self._parameters) != len(expected_param_types):
            msg = "Message did not have the correct number of parameters"
            msg += " (" + str(len(expected_param_types)) + ")"
            raise ValueError(msg)

        for i in range(len(self._parameters)):
            if expected_param_types[i] == int:
                if TypeHelper._is_integer(self._parameters[i]) is False:
                    msg = "Expected integer parameter could not be parsed"
                    raise ValueError(msg)

            elif expected_param_types[i] == float:
                if TypeHelper._is_float(self._parameters[i]) is False:
                    msg = "Expected float parameter could not be parsed"
                    raise ValueError(msg)

        return True

    def message_id(self):
        return self._message_id

    def message_id_name(self):
        return self._message_names[self._message_id]

    def message_friendly_string(self):
        result = self.message_id_name()

        for param in self._parameters:
            result += " "
            result += str(param)

        return result

    def parameters(self):
        return self._parameters
