from .request_client import RequestClient

from pitop.utils.ptdm_message import Message


class PTOLEDManagerException(Exception):
    pass


def set_oled_control_to_pi():
    request_client = RequestClient()

    request_client.init()

    message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, ["1"])
    response = request_client.send_message(message)

    request_client.cleanup()

    if response.message_id() != Message.RSP_SET_OLED_CONTROL:
        raise PTOLEDManagerException("Unable to take control of OLED from MCU")
