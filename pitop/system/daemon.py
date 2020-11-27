from pitopcommon.ptdm_request_client import PTDMRequestClient
from pitopcommon.ptdm_message import Message


def ping():
    message = Message.from_parts(Message.REQ_PING, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    if response.message_id() != Message.RSP_PING:
        raise Exception("Unable to ping pt-device-manager")

    return response.parameters[0]
