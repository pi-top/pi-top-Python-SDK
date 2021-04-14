from .webserver import WebServer
from .blueprints.controller import ControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        camera=None,
        handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprint=ControllerBlueprint(camera=camera, handlers=handlers),
            **kwargs
        )
