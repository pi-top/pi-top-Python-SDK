from .webserver import WebServer
from .blueprints.controller import ControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        camera=None,
        pubsub_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprint=ControllerBlueprint(
                camera=camera, pubsub_handlers=pubsub_handlers),
            **kwargs
        )
