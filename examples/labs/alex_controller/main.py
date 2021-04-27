from pitop import DriveController, PanTiltController, Camera
from pitop.labs import RoverWebController

drive = DriveController()
pan_tilt = PanTiltController()
camera = Camera()

alex_controller = RoverWebController(
    get_frame=camera.get_frame,
    drive=drive,
    pan_tilt=pan_tilt
)

alex_controller.serve_forever()
