from pitop.labs.web.blueprints.controller import ControllerBlueprint

from flask import Blueprint
import math


class RobotDriveControllerBlueprint(Blueprint):
    def __init__(
        self,
        video_feed=None,
        message_handlers={},
        **kwargs
    ):
        Blueprint.__init__(
            self,
            "alex",
            __name__,
            template_folder="templates",
            **kwargs
        )

        self.controller_blueprint = ControllerBlueprint(
            video_feed=video_feed, message_handlers=message_handlers)

    def register(self, app, options, *args, **kwargs):
        app.register_blueprint(self.controller_blueprint, **options)
        Blueprint.register(self, app, options, *args, **kwargs)
