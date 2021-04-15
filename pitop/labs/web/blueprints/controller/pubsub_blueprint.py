from flask import Blueprint, current_app as app
import json
from inspect import getfullargspec, ismethod

pubsub_blueprint = Blueprint('pubsub', __name__)


def log_unhandled_message(message_type, message_data):
    if message_data is None:
        print(f"Unhandled message \"{message_type}\"")
        return

    pretty_message_data = json.dumps(message_data, indent=4, sort_keys=True)
    print(f"Unhandled message \"{message_type}\": {pretty_message_data}")


def handle_message(message, send):
    parsed_message = json.loads(message)

    message_type = parsed_message.get('type', '')
    message_data = parsed_message.get('data')

    message_handlers = app.config.get('message_handlers', {})
    handler = message_handlers.get(message_type)

    if handler is None:
        log_unhandled_message(message_type, message_data)
        return

    spec = getfullargspec(handler)
    if (
        (len(spec.args) == 3 and ismethod(handler))
        or (len(spec.args) == 2 and not ismethod(handler))
        or spec.varargs
    ):
        handler(message_data, send)
        return

    if (
        (len(spec.args) == 2 and ismethod(handler))
        or (len(spec.args) == 1 and not ismethod(handler))
    ):
        handler(message_data)
        return

    handler()


@pubsub_blueprint.route('/pubsub')
def pubsub(ws):
    def send(response_message):
        ws.send(json.dumps(response_message))

    while not ws.closed:
        message = ws.receive()
        if message:
            handle_message(message, send)
