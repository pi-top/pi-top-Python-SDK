from pitopcommon.singleton import Singleton
from pitop.core.mixins import (
    Componentable,
    SupportsBattery,
    SupportsMiniscreen,
)


class Pitop(SupportsMiniscreen, SupportsBattery, Componentable, metaclass=Singleton):
    """Represents a pi-top Device.

    When creating a `Pitop` object, multiple properties will be set,
    depending on the pi-top device that it's running the code. For example, if run on
    a pi-top [4], a `miniscreen` attribute will be created as an interface to control the
    miniscreen OLED display, but that won't be available for other pi-top devices.

    The Pitop class is a Singleton. This means that only one instance per process will
    be created. In practice, this means that if in a particular project you instance a Pitop
    class in 2 different files, they will share the internal state.
    """

    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        Componentable.__init__(self)
