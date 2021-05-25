from pitopcommon.singleton import Singleton
from pitop.core.mixins import (
    Componentable,
    SupportsBattery,
    SupportsMiniscreen,
)
from typing import Optional
from pitop import DriveController, Camera, PanTiltController


class Pitop(SupportsMiniscreen, SupportsBattery, Componentable, metaclass=Singleton):
    """Represents a pi-top Device.

    When creating a `Pitop` object, multiple properties will be set,
    depending on the pi-top device that it's running the code. For example, if run on
    a pi-top [4], a `miniscreen` attribute will be created as an interface to control the
    miniscreen OLED display, but that won't be available for other pi-top devices.

    The Pitop class is a Singleton. This means that only one instance per process will
    be created. In practice, this means that if in a particular project you instance a Pitop
    class in 2 different files, they will share the internal state.

    *property* miniscreen
        If using a pi-top [4], this property returns a :class:`pitop.miniscreen.Miniscreen` object, to interact with
        the device's Miniscreen.


    *property* oled
        Refer to `miniscreen`.


    *property* battery
        If using a pi-top with a battery, this property returns a :class:`pitop.battery.Battery` object, to interact
        with the device's battery.


    *property* drive
        Convenience property to provide autocomplete and introspection functionality in common IDEs.
        If you have not used the `add_component` or `from_config` methods to add a `DriveController` object and you try
        to run your program with this property, an exception will be raised.


    *property* camera
        Convenience property to provide autocomplete and introspection functionality in common IDEs.
        If you have not used the `add_component` or `from_config` methods to add a `Camera` object and you try to run
        your program with this property, an exception will be raised.


    *property* pan_tilt
        Convenience property to provide autocomplete and introspection functionality in common IDEs.
        If you have not used the `add_component` or `from_config` methods to add a `PanTiltController` object and you
        try to run your program with this property, an exception will be raised.
    """
    drive: Optional[DriveController]
    camera: Optional[Camera]
    pan_tilt: Optional[PanTiltController]

    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        Componentable.__init__(self)
