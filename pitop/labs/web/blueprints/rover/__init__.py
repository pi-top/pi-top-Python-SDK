from flask import Blueprint, g
from pitop.labs.web.blueprints.controller import ControllerBlueprint

from .helpers import calculate_velocity_twist, calculate_pan_tilt_angle


class RoverControllerBlueprint(Blueprint):
    def __init__(
        self,
        drive=None,
        pan_tilt=None,
        get_frame=None,
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

        self.drive = drive
        self.pan_tilt = pan_tilt

        if message_handlers.get('left_joystick') is None:
            message_handlers['left_joystick'] = self.left_joystick

        if message_handlers.get('right_joystick') is None:
            message_handlers['right_joystick'] = self.right_joystick

        # set has_pan_tilt in every request context for use in base_rover.html
        @self.before_app_request
        def set_has_pan_tilt():
            g.has_pan_tilt = self.pan_tilt is not None

        self.controller_blueprint = ControllerBlueprint(
            get_frame=get_frame, message_handlers=message_handlers)

    def register(self, app, options, *args, **kwargs):
        app.register_blueprint(self.controller_blueprint, **options)
        Blueprint.register(self, app, options, *args, **kwargs)

    def right_joystick(self, data):
        velocity_twist = calculate_velocity_twist(data)
        linear = velocity_twist.get('linear', 0)
        angular = velocity_twist.get('angular', 0)

        self.drive.robot_move(linear, angular)

    def left_joystick(self, data):
        angle = calculate_pan_tilt_angle(data)

        self.pan_tilt.pan_servo.target_angle = angle.get('z')
        self.pan_tilt.tilt_servo.target_angle = angle.get('y')
