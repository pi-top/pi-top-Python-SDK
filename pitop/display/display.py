from pitopcommon.ptdm_request_client import PTDMRequestClient
from pitopcommon.ptdm_message import Message


class Display:
    def __do_transaction(self, message, expected_response_id, state_str):
        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        if response.message_id() != expected_response_id:
            raise Exception(f"Unable to {state_str} from pi-top hub")

        return response

    def __get_state(
        self,
        state_str,
        message_id,
        expected_response_id,
        expected_parameter_response_format=[int]
    ):
        response = self.__do_transaction(
            self,
            Message.from_parts(message_id, []),
            expected_response_id,
            state_str
        )

        if not response.validate_parameters(expected_parameter_response_format):
            raise Exception(f"Unable to validate {state_str} from pi-top hub")

        return response.parameters()[0]

    def __set_state(
        self,
        state_str,
        message_id,
        expected_response_id,
        value=None
    ):
        parameters = list() if value is None else [str(value)]
        self.__do_transaction(self,
                              Message.from_parts(message_id, parameters),
                              expected_response_id,
                              state_str
                              )
        return True

    @property
    def brightness(self):
        return self.__get_state(
            state_str="get pi-top display brightness",
            message_id=Message.REQ_GET_BRIGHTNESS,
            expected_response_id=Message.RSP_GET_BRIGHTNESS,
        )

    @brightness.setter
    def brightness(self, value):
        return self.__set_state(
            state_str="set pi-top display brightness",
            message_id=Message.REQ_SET_BRIGHTNESS,
            expected_response_id=Message.RSP_SET_BRIGHTNESS,
            value=value
        )

    def increment_brightness(self):
        return self.__set_state(
            state_str="increment pi-top display brightness",
            message_id=Message.REQ_INCREMENT_BRIGHTNESS,
            expected_response_id=Message.RSP_INCREMENT_BRIGHTNESS
        )

    def decrement_brightness(self):
        return self.__set_state(
            state_str="decrement pi-top display brightness",
            message_id=Message.REQ_DECREMENT_BRIGHTNESS,
            expected_response_id=Message.RSP_DECREMENT_BRIGHTNESS
        )

    def blank(self):
        return self.__set_state(
            state_str="blank pi-top display",
            message_id=Message.REQ_BLANK_SCREEN,
            expected_response_id=Message.RSP_BLANK_SCREEN
        )

    def unblank(self):
        return self.__set_state(
            state_str="unblank pi-top display",
            message_id=Message.REQ_UNBLANK_SCREEN,
            expected_response_id=Message.RSP_UNBLANK_SCREEN
        )

    @property
    def blanking_timeout(self):
        return self.__get_state(
            state_str="pi-top display blanking timeout",
            message_id=Message.REQ_GET_SCREEN_BLANKING_TIMEOUT,
            expected_response_id=Message.RSP_GET_SCREEN_BLANKING_TIMEOUT,
        )

    @blanking_timeout.setter
    def blanking_timeout(self, value):
        if value < 0:
            raise Exception("Cannot set timeout < 0")

        if value % 60 != 0:
            raise Exception("Timeout must be a multiple of 60")

        return self.__set_state(
            state_str="set pi-top display blanking timeout",
            message_id=Message.REQ_UNBLANK_SCREEN,
            expected_response_id=Message.RSP_UNBLANK_SCREEN,
            value=value
        )

    @property
    def backlight(self):
        return self.__get_state(
            state_str="get pi-top display backlight state",
            message_id=Message.REQ_GET_SCREEN_BACKLIGHT_STATE,
            expected_response_id=Message.RSP_GET_SCREEN_BACKLIGHT_STATE,
        )

    @backlight.setter
    def backlight(self, value):
        assert type(value) is bool
        str_val = "1" if value is True else "0"
        return self.__set_state(
            state_str="set pi-top display backlight state",
            value=str_val,
            message_id=Message.REQ_SET_SCREEN_BACKLIGHT_STATE,
            expected_response_id=Message.RSP_SET_SCREEN_BACKLIGHT_STATE,
        )

    @property
    def lid(self):
        return self.__get_state(
            state_str="get pi-top display lid open state",
            message_id=Message.REQ_GET_LID_OPEN_STATE,
            expected_response_id=Message.RSP_GET_LID_OPEN_STATE,
        )
