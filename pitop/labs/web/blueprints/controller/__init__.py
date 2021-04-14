from flask import Blueprint

from .publish_blueprint import publish_blueprint
from .video_blueprint import video_blueprint


class ControllerBlueprint(Blueprint):
    def __init__(self, camera=None, handlers={}, **kwargs):
        Blueprint.__init__(
            self,
            "controller",
            __name__,
            template_folder="templates",
            static_folder="static",
            **kwargs
        )

        self.handlers = handlers
        self.camera = camera

    def register(self, app, options, *args, **kwargs):
        sockets = options.get('sockets')
        if sockets is None:
            raise Exception(
                'sockets must be passed to register_blueprint to register ControllerBlueprint')

        # setup custom config
        app.config['handlers'] = self.handlers
        app.config['camera'] = self.camera

        # register child blueprints
        sockets.register_blueprint(publish_blueprint)
        app.register_blueprint(video_blueprint)

        # register self
        Blueprint.register(self, app, options, **kwargs)
