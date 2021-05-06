from flask import Blueprint

from pitop.labs.web.blueprints.base import BaseBlueprint
from pitop.labs.web.blueprints.webcomponents import WebComponentsBlueprint
from pitop.labs.web.blueprints.messaging import MessagingBlueprint
from pitop.labs.web.blueprints.video import VideoBlueprint


class ControllerBlueprint(Blueprint):
    def __init__(self, get_frame=None, message_handlers={}, **kwargs):
        Blueprint.__init__(
            self,
            "controller",
            __name__,
            template_folder="templates",
            static_folder="static",
            **kwargs
        )

        self.base_blueprint = BaseBlueprint()
        self.components_blueprint = WebComponentsBlueprint()
        self.video_blueprint = VideoBlueprint(get_frame=get_frame)
        self.messaging_blueprint = MessagingBlueprint(
            message_handlers=message_handlers)

    def register(self, app, options, *args, **kwargs):
        # register child blueprints
        app.register_blueprint(self.base_blueprint, **options)
        app.register_blueprint(self.components_blueprint, **options)
        app.register_blueprint(self.video_blueprint, **options)
        app.register_blueprint(self.messaging_blueprint, **options)

        # register self
        Blueprint.register(self, app, options, *args, **kwargs)

    def broadcast(self, message):
        self.messaging_blueprint.broadcast(message)
