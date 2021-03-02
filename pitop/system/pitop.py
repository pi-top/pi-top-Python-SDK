from pitopcommon.singleton import Singleton
from pitop.core.mixins import (
    SupportsMiniscreen,
    SupportsBattery,
)
from pitop.core.mixins import Componentable


class PiTop(SupportsMiniscreen, SupportsBattery, Componentable, metaclass=Singleton):
    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        Componentable.__init__(self)
