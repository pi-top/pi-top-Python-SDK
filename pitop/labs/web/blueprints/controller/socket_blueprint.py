from flask import Blueprint, current_app as app
import json

socket_blueprint = Blueprint('controller_socket', __name__)


def handle_command(message):
    parsed_message = json.loads(message)

    message_type = parsed_message.get('type', '')
    message_data = parsed_message.get('data', dict())

    handlers = app.config.get('handlers', {})
    handler = handlers.get(message_type)
    if handler:
        return handler(message_data)

    pretty_message_data = json.dumps(message_data, indent=4, sort_keys=True)
    print(f"Unhandled message \"{message_type}\": {pretty_message_data}")


@socket_blueprint.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            handle_command(message)
    print('Command socket disconnected')
