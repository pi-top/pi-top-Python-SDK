from pitop.miniscreen.oled import (  # noqa: F401
    OLED as PTOLEDDisplay,
    canvas,
    # oled_image,  # TODO: re-add
)
from pitop.miniscreen.oled.core import (  # noqa: F401
    display,
    fps_regulator,
)
from pitop.miniscreen.oled.core.controls import (  # noqa: F401
    get_oled_device as get_device_instance,
    oled_device_is_active as device_reserved,
    reset_oled_device as reset_device_instance,
    set_oled_control_to_pi,
    set_oled_control_to_hub
)
from pitop.miniscreen.oled import controls as device_helper  # noqa: F401

print("Note: Use of the 'ptoled' package is now deprecated. Please use 'pitop.miniscreen.oled' instead.")
# TODO
print("For more information, please see <TODO: URL>")
