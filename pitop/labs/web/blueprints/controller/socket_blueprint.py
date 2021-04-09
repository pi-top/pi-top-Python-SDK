from flask import Blueprint, current_app as app
import json

socket_blueprint = Blueprint('controller_socket', __name__)


def handle_command(message):
    parsed_message = json.loads(message)

    message_type = parsed_message.get('type', '')

    handlers = app.config.get('handlers', {})
    handler = handlers.get(message_type)

    if handler is None:
        pretty_message_data = json.dumps(message_data, indent=4, sort_keys=True)
        print(f"Unhandled message \"{message_type}\": {pretty_message_data}")
        return

    message_data = parsed_message.get('data')

    if message_data:
        return handler(message_data)

    return handler()


@socket_blueprint.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            handle_command(message)
    print('Command socket disconnected')
