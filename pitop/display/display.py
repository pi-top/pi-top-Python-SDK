from pitopcommon.ptdm import (
    PTDMRequestClient,
    PTDMSubscribeClient,
    Message,
)
import atexit


class Display:
    def __init__(self):
        self.when_brightness_changed = None
        self.when_screen_blanked = None
        self.when_screen_unblanked = None
        self.when_lid_closed = None
        self.when_lid_opened = None

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def on_brightness_changed(parameters):
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_brightness_changed, parameters[0])

        def on_screen_blanked():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_screen_blanked)

        def on_screen_unblanked():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_screen_unblanked)

        def on_lid_closed():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_lid_closed)

        def on_lid_opened():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_lid_opened)

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise({
            Message.PUB_BRIGHTNESS_CHANGED: on_brightness_changed,
            Message.PUB_SCREEN_BLANKED: on_screen_blanked,
            Message.PUB_SCREEN_UNBLANKED: on_screen_unblanked,
            Message.PUB_LID_CLOSED: on_lid_closed,
            Message.PUB_LID_OPENED: on_lid_opened,
        })

        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    def __do_transaction(self, message, state_str):
        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        return response

    def __get_state(
        self,
        state_str,
        message_id,
    ):
        response = self.__do_transaction(
            Message.from_parts(message_id, []),
            state_str
        )

        return response.parameters[0]

    def __set_state(
        self,
        state_str,
        message_id,
        value=None
    ):
        parameters = list() if value is None else [str(value)]
        self.__do_transaction(Message.from_parts(message_id, parameters),
                              state_str
                              )
        return True

    @property
    def brightness(self):
        return int(
            self.__get_state(
                state_str="get pi-top display brightness",
                message_id=Message.REQ_GET_BRIGHTNESS,
            )
        )

    @brightness.setter
    def brightness(self, value):
        return self.__set_state(
            state_str="set pi-top display brightness",
            message_id=Message.REQ_SET_BRIGHTNESS,
            value=value
        )

    def increment_brightness(self):
        return self.__set_state(
            state_str="increment pi-top display brightness",
            message_id=Message.REQ_INCREMENT_BRIGHTNESS,
        )

    def decrement_brightness(self):
        return self.__set_state(
            state_str="decrement pi-top display brightness",
            message_id=Message.REQ_DECREMENT_BRIGHTNESS,
        )

    def blank(self):
        return self.__set_state(
            state_str="blank pi-top display",
            message_id=Message.REQ_BLANK_SCREEN,
        )

    def unblank(self):
        return self.__set_state(
            state_str="unblank pi-top display",
            message_id=Message.REQ_UNBLANK_SCREEN,
        )

    @property
    def blanking_timeout(self):
        return int(
            self.__get_state(
                state_str="pi-top display blanking timeout",
                message_id=Message.REQ_GET_SCREEN_BLANKING_TIMEOUT,
            )
        )

    @blanking_timeout.setter
    def blanking_timeout(self, value):
        if value < 0:
            raise Exception("Cannot set timeout < 0")

        if value % 60 != 0:
            raise Exception("Timeout must be a multiple of 60")

        return self.__set_state(
            state_str="set pi-top display blanking timeout",
            message_id=Message.REQ_SET_SCREEN_BLANKING_TIMEOUT,
            value=value
        )

    @property
    def backlight(self):
        return int(
            self.__get_state(
                state_str="get pi-top display backlight state",
                message_id=Message.REQ_GET_SCREEN_BACKLIGHT_STATE,
            )
        ) == 1

    @backlight.setter
    def backlight(self, value):
        assert type(value) is bool
        str_val = "1" if value is True else "0"
        return self.__set_state(
            state_str="set pi-top display backlight state",
            value=str_val,
            message_id=Message.REQ_SET_SCREEN_BACKLIGHT_STATE,
        )

    @property
    def lid_is_open(self):
        return int(
            self.__get_state(
                state_str="get pi-top display lid open state",
                message_id=Message.REQ_GET_LID_OPEN_STATE,
            )
        ) == 1
