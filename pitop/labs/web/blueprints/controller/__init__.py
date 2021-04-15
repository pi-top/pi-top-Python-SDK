from flask import Blueprint

from .pubsub_blueprint import pubsub_blueprint
from .video_blueprint import video_blueprint


class ControllerBlueprint(Blueprint):
    def __init__(self, camera=None, message_handlers={}, **kwargs):
        Blueprint.__init__(
            self,
            "controller",
            __name__,
            template_folder="templates",
            static_folder="static",
            **kwargs
        )

        self.message_handlers = message_handlers
        self.camera = camera

    def register(self, app, options, *args, **kwargs):
        sockets = options.get('sockets')
        if sockets is None:
            raise Exception(
                'sockets must be passed to register_blueprint to register ControllerBlueprint')

        # setup custom config
        app.config['message_handlers'] = self.message_handlers
        app.config['camera'] = self.camera

        # register child blueprints
        sockets.register_blueprint(pubsub_blueprint)
        app.register_blueprint(video_blueprint)

        # register self
        Blueprint.register(self, app, options, **kwargs)
