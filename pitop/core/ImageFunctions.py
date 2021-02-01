from PIL import Image
from cv2 import (
    cvtColor,
    COLOR_BGR2RGB,
    COLOR_RGB2BGR,
)
from numpy import (
    asarray,
    ndarray,
)
from urllib.request import urlopen

from pitopcommon.formatting import is_url


def __image_has_3_channels(image):
    if not isinstance(image, ndarray):
        image = asarray(image)
    return len(image.shape) > 2 and image.shape[2] == 3


def convert(image, format="PIL"):
    assert isinstance(format, str)
    format = format.lower()
    assert format in ("pil", "opencv")

    if ([
        isinstance(image, Image.Image) and format == "pil",
        isinstance(image, ndarray) and format == "opencv"
    ]):
        return image
    elif isinstance(image, Image.Image) and format == "opencv":
        image = asarray(image)
        if __image_has_3_channels(image) and image.mode == "RGB":
            image = cvtColor(image, COLOR_RGB2BGR)
        return image
    elif isinstance(image, ndarray) and format == "pil":
        if __image_has_3_channels(image):
            image = cvtColor(image, COLOR_BGR2RGB)
        return Image.fromarray(image)


def get_pil_image_from_path(file_path_or_url):
    if is_url(file_path_or_url):
        image_path = urlopen(file_path_or_url)
    else:
        image_path = file_path_or_url

    image = Image.open(image_path)

    # Verify on deep copy to avoid needing to close and
    # re-open after verifying...
    test_image = image.copy()
    # Raise exception if there's an issue with the image
    test_image.verify()

    return image
