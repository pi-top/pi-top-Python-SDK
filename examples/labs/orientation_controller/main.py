import os

from pitop import Camera, DriveController, Pitop
from pitop.labs import RoverWebController

# to access device orientation sensors, the webpage must be accessed over ssl,
# so ensure that an ssl cert exists for this
if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
    print("Generating self-signed ssl cert")
    os.system(
        'openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -nodes -subj "/O=pi-top"'
    )

rover = Pitop()
rover.add_component(DriveController())
rover.add_component(Camera())


def device_orientation(data):
    print(data)
    x = data.get("x", 0)
    y = data.get("y", 0)

    if abs(x) < 5:
        x = 0
    x = x * -0.1

    if abs(y) < 5:
        y = 0
    y = y * 0.1

    print(x, y)
    rover.drive.robot_move(y, x)


rover_controller = RoverWebController(
    get_frame=rover.camera.get_frame,
    drive=rover.drive,
    message_handlers={"device_orientation": device_orientation},
    cert="cert.pem",
    key="key.pem",
)

rover_controller.serve_forever()
