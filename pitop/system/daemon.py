from pitopcommon.ptdm import PTDMRequestClient, Message


def ping():
    message = Message.from_parts(Message.REQ_PING, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    return response.parameters[0]


def set_oled_spi_port(port):
    message = Message.from_parts(Message.REQ_SET_OLED_SPI_IN_USE, [str(port)])

    with PTDMRequestClient() as request_client:
        request_client.send_message(message)


def get_oled_spi_port():
    message = Message.from_parts(Message.REQ_GET_OLED_SPI_IN_USE, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    return int(response.parameters()[0])
