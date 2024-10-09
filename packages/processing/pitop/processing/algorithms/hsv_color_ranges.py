import logging
from typing import Optional, Union

from ..core.vision_functions import hsv_to_rgb

logger = logging.getLogger(__name__)


class HSVColorRanges:
    ranges = {
        "red": [
            {"lower": (0, 100, 100), "upper": (5, 255, 255)},
            {"lower": (150, 100, 100), "upper": (179, 255, 255)},
        ],
        "green": [{"lower": (60, 100, 100), "upper": (90, 255, 255)}],
        "blue": [{"lower": (100, 100, 100), "upper": (130, 255, 255)}],
        "yellow": [{"lower": (20, 100, 100), "upper": (40, 255, 255)}],
    }

    @classmethod
    def supported(cls):
        return list(cls.ranges.keys())

    @classmethod
    def is_supported(cls, color: str) -> bool:
        return color in cls.ranges

    @classmethod
    def get_color_for_hsv_limits(cls, lower: tuple, upper: tuple) -> Optional[str]:
        # find the color name associated to the lower and upper HSV values, if they exist
        def arrays_match(a, b):
            return len(a) == len(b) and all(a[i] == b[i] for i in range(len(a)))

        for color, ranges_arr in cls.ranges.items():
            for range_item in ranges_arr:
                if arrays_match(range_item["lower"], lower) and arrays_match(
                    range_item["upper"], upper
                ):
                    return color

    @classmethod
    def get(cls, color: str) -> Optional[list]:
        return cls.ranges.get(color)

    @classmethod
    def add(cls, color: str, lower: Union[tuple, list], upper: Union[tuple, list]):
        if not all(isinstance(i, tuple) or isinstance(i, list) for i in (lower, upper)):
            raise ValueError("Lower and upper must be tuples")

        if color not in cls.ranges:
            cls.ranges[color] = []
        cls.ranges[color].append({"lower": tuple(lower), "upper": tuple(upper)})
        logger.info(f"Added color {color} with lower {lower} and upper {upper}")

    @classmethod
    def validate(cls, color_arg: Union[str, list]) -> list:
        colors = []
        supported_colors = cls.supported()
        if isinstance(color_arg, str):
            colors = [color_arg]
        elif type(color_arg) in (list, tuple):
            colors = color_arg
        if not set(colors).issubset(supported_colors):
            raise ValueError(
                f"Valid color values are {', '.join(supported_colors[:-1])} or {supported_colors[-1]}"
            )
        return colors

    @classmethod
    def to_rgb(cls, color_name: str) -> list:
        color = cls.get(color_name)
        if color is None:
            raise Exception(f"Color '{color_name}' not found")
        hsv_arr = list()
        for hsv_lower_upper in color:
            for hsv in hsv_lower_upper.values():
                hsv_arr.append(list(hsv))
        return hsv_to_rgb(hsv_arr)

    @classmethod
    def to_bgr(cls, color_name: str) -> list:
        rgb = cls.to_rgb(color_name)
        return rgb[::-1]
