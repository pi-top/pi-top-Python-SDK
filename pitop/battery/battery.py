from pitopcommon.ptdm_request_client import PTDMRequestClient
from pitopcommon.ptdm_message import Message


class Battery:
    def full_state(self):
        message = Message.from_parts(Message.REQ_GET_BATTERY_STATE, [])

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        if response.message_id() != Message.RSP_GET_BATTERY_STATE:
            raise Exception("Unable to get battery state from pi-top hub")

        if not response.validate_parameters([int, int, int, int]):
            raise Exception("Unable to get valid battery information from pi-top hub")

        return response.parameters()

    def charging_state(self):
        __charging_state, _, _, _ = self.full_state()
        return __charging_state

    def capacity(self):
        _, __capacity, _, _ = self.full_state()
        return __capacity

    def time_remaining(self):
        _, _, __time_remaining, _ = self.full_state()
        return __time_remaining

    def wattage(self):
        _, _, _, __wattage = self.full_state()
        return __wattage
