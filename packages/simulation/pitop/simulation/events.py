from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class SimEventTypes(Enum):
    SLIDER_UPDATE = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()


@dataclass
class SimEvent:
    type: SimEventTypes
    target_name: Optional[str] = None
    value: Any = None
