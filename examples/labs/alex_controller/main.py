from pitop import DriveController, PanTiltController, Camera
from pitop.labs import WebServer, AlexControllerBlueprint

drive = DriveController()
pan_tilt = PanTiltController()
camera = Camera()

alex_controller = WebServer(
    blueprint=AlexControllerBlueprint(
        camera=camera,
        drive=drive,
        pan_tilt=pan_tilt
    )
)

alex_controller.serve_forever()
