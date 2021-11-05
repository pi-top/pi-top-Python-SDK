from pitop.common.ptdm import Message, PTDMRequestClient


def ping():
    message = Message.from_parts(Message.REQ_PING, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    return int(response.parameters[0]) == 1
