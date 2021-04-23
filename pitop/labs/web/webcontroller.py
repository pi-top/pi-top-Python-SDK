from .webserver import WebServer
from .blueprints import ControllerBlueprint, RobotDriveControllerBlueprint


class WebController(WebServer):
    def __init__(
        self,
        video_feed=None,
        message_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprints=[ControllerBlueprint(
                video_feed=video_feed,
                message_handlers=message_handlers
            )],
            **kwargs
        )


class RobotDriveWebController(WebServer):
    def __init__(
        self,
        video_feed=None,
        left_joystick=None,
        right_joystick=None,
        message_handlers={},
        **kwargs
    ):
        WebServer.__init__(
            self,
            blueprints=[RobotDriveControllerBlueprint(
                video_feed=video_feed,
                left_joystick=left_joystick,
                right_joystick=right_joystick,
                message_handlers=message_handlers
            )],
            **kwargs
        )
