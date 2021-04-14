from .webserver import WebServer
from .blueprints import ControllerBlueprint, AlexControllerBlueprint


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


class AlexWebController(WebServer):
    def __init__(
        self,
        camera=None,
        drive=None,
        pan_tilt=None,
        pubsub_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprint=AlexControllerBlueprint(
                camera=camera,
                drive=drive,
                pan_tilt=pan_tilt,
                pubsub_handlers=pubsub_handlers),
            **kwargs
        )
