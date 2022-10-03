import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from .mock_hardware import is_virtual_hardware, use_virtual_hardware  # noqa: E402
from .simulation.simulation import simulate  # noqa: E402
