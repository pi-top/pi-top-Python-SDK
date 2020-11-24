from .request_client import RequestClient

from pitoputils.ptdm_message import Message


class MiniScreenOLEDManagerException(Exception):
    pass


def set_oled_control_to_pi():
    request_client = RequestClient()

    request_client.init()

    message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, ["1"])
    response = request_client.send_message(message)

    request_client.cleanup()

    if response.message_id() != Message.RSP_SET_OLED_CONTROL:
        raise MiniScreenOLEDManagerException("Unable to take control of OLED from pi-top hub")
