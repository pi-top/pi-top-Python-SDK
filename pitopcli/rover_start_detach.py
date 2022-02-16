import sys

from pitop import Camera, DriveController, Pitop
from pitop.common.formatting import is_url
from pitop.common.sys_info import get_internal_ip
from pitop.labs import RoverWebController

try:
    port = int(sys.argv[1])
except Exception:
    port = None

rover = Pitop()
rover.add_component(DriveController())
rover.add_component(Camera())

rover_controller = RoverWebController(
    port=port,
    get_frame=rover.camera.get_frame,
    drive=rover.drive,
)

for interface in ("wlan0", "ptusb0", "lo", "en0"):
    ip_address = get_internal_ip(interface)
    if is_url("http://" + ip_address):
        break

text = f"Rover Remote Control:\nhttp://\n{ip_address}:{port}"
rover.miniscreen.display_text(text, font_size=12)

rover_controller.serve_forever()
