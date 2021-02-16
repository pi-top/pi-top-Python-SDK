from pitopcommon.singleton import Singleton
from pitop.core.mixins import (
    ManagesPMAComponents,
    SupportsBattery,
    SupportsMiniscreen,
)


class PiTop(SupportsMiniscreen, SupportsBattery, ManagesPMAComponents, metaclass=Singleton):
    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        ManagesPMAComponents.__init__(self)
