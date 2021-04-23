from flask import Blueprint

from pitop.labs.web.blueprints.base import BaseBlueprint
from pitop.labs.web.blueprints.messaging import MessagingBlueprint
from pitop.labs.web.blueprints.video import VideoBlueprint


class ControllerBlueprint(Blueprint):
    def __init__(
        self,
        blueprint_id="controller",
        inputs={},
        outputs={},
        **kwargs
    ):
        Blueprint.__init__(
            self,
            blueprint_id,
            __name__,
            template_folder="templates",
            static_folder="static",
            **kwargs
        )

        self.base_blueprint = BaseBlueprint()

        self.video_blueprints = list()
        for k, v in inputs.items():
            if k.startswith("video"):
                self.video_blueprints.append(
                    VideoBlueprint(
                        name=k, video_input=v
                    )
                )

        self.messaging_blueprint = MessagingBlueprint(
            outputs=outputs)

    def register(self, app, options, *args, **kwargs):
        # register child blueprints
        app.register_blueprint(self.base_blueprint, **options)

        for video_blueprint in self.video_blueprints:
            app.register_blueprint(video_blueprint, **options)

        app.register_blueprint(self.messaging_blueprint, **options)

        # register self
        Blueprint.register(self, app, options, *args, **kwargs)
