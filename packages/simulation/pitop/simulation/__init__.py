import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from .simulation import simulate  # noqa: E402
from .virtual_hardware import is_virtual_hardware, use_virtual_hardware  # noqa: E402
