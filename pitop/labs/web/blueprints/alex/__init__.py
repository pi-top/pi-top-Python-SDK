from flask import Blueprint
from pitop.labs.web.blueprints.controller import ControllerBlueprint

from .helpers import calculate_velocity_twist, calculate_pan_tilt_angle


class AlexControllerBlueprint(Blueprint):
    def __init__(
        self,
        drive=None,
        pan_tilt=None,
        camera=None,
        handlers={},
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
        self.controller_blueprint = ControllerBlueprint(
            camera=camera, handlers=handlers)

    def register(self, app, options, *args, **kwargs):
        app.register_blueprint(self.controller_blueprint, **options)

        handlers = app.config.get('handlers', {})

        if handlers.get('left_joystick') is None:
            handlers['left_joystick'] = self.left_joystick

        if handlers.get('right_joystick') is None:
            handlers['right_joystick'] = self.right_joystick

        app.config['handlers'] = handlers

        Blueprint.register(self, app, options, *args, **kwargs)

    def left_joystick(self, data):
        velocity_twist = calculate_velocity_twist(data)
        linear = velocity_twist.get('linear', 0)
        angular = velocity_twist.get('angular', 0)

        self.drive.robot_move(linear, angular)

    def right_joystick(self, data):
        angle = calculate_pan_tilt_angle(data)

        self.pan_tilt.pan_servo.target_angle = angle.get('z')
        self.pan_tilt.tilt_servo.target_angle = angle.get('y')
