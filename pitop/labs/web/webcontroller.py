from .webserver import WebServer
from .blueprints import ControllerBlueprint, AlexControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        get_frame=None,
        message_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprints=[ControllerBlueprint(
                get_frame=get_frame,
                message_handlers=message_handlers
            )],
            **kwargs
        )


class AlexWebController(WebServer):
    def __init__(
        self,
        get_frame=None,
        drive=None,
        pan_tilt=None,
        message_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprints=[AlexControllerBlueprint(
                get_frame=get_frame,
                drive=drive,
                pan_tilt=pan_tilt,
                message_handlers=message_handlers
            )],
            **kwargs
        )
