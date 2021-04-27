from pitop import Pitop, alex_config
from pitop.labs import RoverWebController

alex = Pitop.from_config(alex_config)

alex_controller = RoverWebController(
    get_frame=alex.camera.get_frame,
    drive=alex.drive,
    pan_tilt=alex.pan_tilt
)

alex_controller.serve_forever()
