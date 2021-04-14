from pitop import DriveController, PanTiltController, Camera
from pitop.labs import AlexWebController

drive = DriveController()
pan_tilt = PanTiltController()
camera = Camera()

alex_controller = AlexWebController(
    camera=camera,
    drive=drive,
    pan_tilt=pan_tilt
)

alex_controller.serve_forever()
