from pitopcommon.logger import PTLogger
from pitopcommon.ptdm import (
    PTDMRequestClient,
    PTDMSubscribeClient,
    Message,
)

import atexit


class Battery:
    def __init__(self):
        # Battery capacity change events from ptdm
        self.when_low = None
        self.when_critical = None

        # Battery full capacity as charging state change event from ptdm
        self.when_full = None

        # Internal battery charging state change events
        self.when_charging = None
        self.when_discharging = None

        self.__previous_charging_state = Battery.get_full_state()[0]

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def on_state_changed(parameters):
            charging_state = int(parameters[0])

            if charging_state not in range(0, 3):
                PTLogger.warning("Invalid charging state from pi-top device manager")
                return

            if charging_state == self.__previous_charging_state:
                PTLogger.debug("Charging state has not changed - doing nothing...")
                return

            self.__previous_charging_state = charging_state

            funcs_to_invoke = {
                2: self.when_full,
                1: self.when_charging,
                0: self.when_discharging,
            }

            func = funcs_to_invoke[charging_state]

            if callable(func):
                func()

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise({
            Message.PUB_LOW_BATTERY_WARNING: lambda: self.when_low,
            Message.PUB_CRITICAL_BATTERY_WARNING: lambda: self.when_critical,
            Message.PUB_BATTERY_STATE_CHANGED: on_state_changed,
        })
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    @classmethod
    def get_full_state(cls):
        message = Message.from_parts(Message.REQ_GET_BATTERY_STATE, [])

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        return response.parameters

    @property
    def is_charging(self):
        __charging_state, _, _, _ = Battery.get_full_state()
        return __charging_state != "0"

    @property
    def is_full(self):
        __charging_state, _, _, _ = Battery.get_full_state()
        return __charging_state == "2"

    @property
    def capacity(self):
        _, __capacity, _, _ = Battery.get_full_state()
        return int(__capacity)

    @property
    def time_remaining(self):
        _, _, __time_remaining, _ = Battery.get_full_state()
        return int(__time_remaining)

    @property
    def wattage(self):
        _, _, _, __wattage = Battery.get_full_state()
        return int(__wattage)
