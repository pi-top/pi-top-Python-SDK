import json
from inspect import getfullargspec, ismethod
from time import time

from flask import Blueprint


def log_unhandled_message(message_type, message_data):
    if message_data is None:
        print(f'Unhandled message "{message_type}"')
        return

    pretty_message_data = json.dumps(message_data, indent=4, sort_keys=True)
    print(f'Unhandled message "{message_type}": {pretty_message_data}')


class MessagingBlueprint(Blueprint):
    def __init__(self, message_handlers=None, **kwargs):
        message_handlers = {} if message_handlers is None else message_handlers
        Blueprint.__init__(
            self,
            "messaging",
            __name__,
            static_folder="messaging",
            template_folder="templates",
            **kwargs,
        )

        def handle_message(message, send):
            parsed_message = json.loads(message)

            message_type = parsed_message.get("type", "")
            message_data = parsed_message.get("data")

            handler = message_handlers.get(message_type)

            if handler is None:
                log_unhandled_message(message_type, message_data)
                return

            spec = getfullargspec(handler)
            if len(spec.args) == (3 if ismethod(handler) else 2) or spec.varargs:
                handler(message_data, send)
                return

            if len(spec.args) == (2 if ismethod(handler) else 1):
                handler(message_data)
                return

            handler()

        self.sockets = {}
        self.socket_blueprint = Blueprint("messaging_socket", __name__)

        @self.socket_blueprint.route("/messaging")
        def pubsub(ws):
            id = time()
            self.sockets[id] = ws

            def send(response_message):
                ws.send(json.dumps(response_message))

            while not ws.closed:
                message = ws.receive()
                if message:
                    handle_message(message, send)

            del self.sockets[id]

    def register(self, app, options, *args):
        Blueprint.register(self, app, options, *args)

        sockets = options.get("sockets")
        if sockets is None:
            raise Exception("Unable to register MessagingBlueprint without sockets")

        sockets.register_blueprint(self.socket_blueprint)

    def broadcast(self, message):
        for socket in self.sockets.values():
            socket.send(json.dumps(message))
