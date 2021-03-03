from json import load
from pathlib import Path

from pitop import Pitop


def AlexRobot():
    return Pitop.from_dict(__load_json('alex.json'))


def __load_json(filename):
    path = __robotics_directory() / "json" / filename
    with open(path, 'r') as handle:
        config = load(handle)
    return config


def __robotics_directory() -> Path:
    return Path(__file__).parent
