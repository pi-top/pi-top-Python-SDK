from .webserver import WebServer
from .blueprints import ControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        video_input=None,
        message_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprints=[ControllerBlueprint(
                video_input=video_input,
                message_handlers=message_handlers
            )],
            **kwargs
        )
