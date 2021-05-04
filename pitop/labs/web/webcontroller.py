from .webserver import WebServer
from .blueprints import ControllerBlueprint, RoverControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        get_frame=None,
        message_handlers={},
        blueprints=[],
        **kwargs
    ):
        self.controller_blueprint = ControllerBlueprint(
            get_frame=get_frame,
            message_handlers=message_handlers
        )

        WebServer.__init__(
            self,
            blueprints=[self.controller_blueprint] + blueprints,
            **kwargs
        )

    def broadcast(self, message):
        self.controller_blueprint.broadcast(message)


class RoverWebController(WebServer):
    def __init__(
        self,
        get_frame=None,
        drive=None,
        pan_tilt=None,
        message_handlers={},
        blueprints=[],
        **kwargs
    ):
        self.rover_blueprint = RoverControllerBlueprint(
            get_frame=get_frame,
            drive=drive,
            pan_tilt=pan_tilt,
            message_handlers=message_handlers
        )

        WebServer.__init__(
            self,
            blueprints=[self.rover_blueprint] + blueprints,
            **kwargs
        )

    def broadcast(self, message):
        self.rover_blueprint.broadcast(message)
