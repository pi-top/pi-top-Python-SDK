from pitopcommon.ptdm import (
    PTDMRequestClient,
    PTDMSubscribeClient,
    Message,
)

import atexit


class Battery:
    def __init__(self):
        self.when_low = None
        self.when_critical = None
        self.when_charging = None
        self.when_discharging = None
        # self.when_capacity_changed = None
        self.when_full = None

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def on_low_battery():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_low)

        def on_critical_battery():
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_critical)

        def on_state_changed(parameters):
            charging_state, capacity, time_remaining, wattage = parameters()

            if charging_state == 2:
                self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_full)

            if charging_state == 0:
                self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_discharging)
            else:
                self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_charging)

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise({
            Message.PUB_LOW_BATTERY_WARNING: on_low_battery,
            Message.PUB_CRITICAL_BATTERY_WARNING: on_critical_battery,
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

        return response.parameters()

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
