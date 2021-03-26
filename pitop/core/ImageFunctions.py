from PIL import Image
from numpy import (
    asarray,
    ndarray,
)
from urllib.request import urlopen

from pitopcommon.formatting import is_url


def image_format_check(format):
    assert isinstance(format, str)
    assert format.lower() in ("pil", "opencv")


def convert(image, format="PIL"):

    try:
        from cv2 import (
            cvtColor,
            COLOR_BGR2RGB,
            COLOR_RGB2BGR,
        )
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "OpenCV Python library is not installed. You can install it by running 'sudo apt install python3-opencv libatlas-base-dev'.") from None

    image_format_check(format)
    format = format.lower()

    # Image type is already correct - return image
    if any([
        isinstance(image, Image.Image) and format == "pil",
        isinstance(image, ndarray) and format == "opencv"
    ]):
        return image
    elif isinstance(image, Image.Image) and format == "opencv":
        # Convert PIL to OpenCV
        cv_image = asarray(image)
        if image.mode == "RGB":
            cv_image = cvtColor(cv_image, COLOR_RGB2BGR)
        return cv_image
    elif isinstance(image, ndarray) and format == "pil":
        # Convert OpenCV to PIL
        if len(image.shape) > 2 and image.shape[2] == 3:
            # If incoming image has 3 channels, convert from BGR to RGB
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
