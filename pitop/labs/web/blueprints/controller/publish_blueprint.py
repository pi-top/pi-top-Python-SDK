from flask import Blueprint, current_app as app
import json
from inspect import getfullargspec

publish_blueprint = Blueprint('publish', __name__)


def log_unhandled_message(message_type, message_data):
    if message_data is None:
        print(f"Unhandled message \"{message_type}\"")
        return

    pretty_message_data = json.dumps(message_data, indent=4, sort_keys=True)
    print(f"Unhandled message \"{message_type}\": {pretty_message_data}")


def handle_message(message, ws):
    parsed_message = json.loads(message)

    message_type = parsed_message.get('type', '')
    message_data = parsed_message.get('data')

    handlers = app.config.get('handlers', {})
    handler = handlers.get(message_type)

    if handler is None:
        log_unhandled_message(message_type, message_data)
        return

    spec = getfullargspec(handler)
    if len(spec.args) == 2 or spec.varargs:
        handler(message_data, ws)
        return

    if len(spec.args) == 1:
        handler(message_data)
        return

    handler()


@publish_blueprint.route('/publish')
def publish(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            handle_message(message, ws)
