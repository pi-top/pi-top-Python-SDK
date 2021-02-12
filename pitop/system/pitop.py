from pitopcommon.singleton import Singleton
from pitop.core.mixins import (
    SupportsAttachingPlates,
    SupportsBattery,
    SupportsMiniscreen,
)


class PiTop(SupportsMiniscreen, SupportsBattery, SupportsAttachingPlates, metaclass=Singleton):
    def __init__(self):
        SupportsMiniscreen.__init__(self)
        SupportsBattery.__init__(self)
        SupportsAttachingPlates.__init__(self)
