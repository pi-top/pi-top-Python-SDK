from urllib.request import urlopen

from numpy import asarray, ndarray
from PIL import Image

from pitop.common.formatting import is_url
from pitop.core.import_opencv import import_opencv


def image_format_check(format):
    assert isinstance(format, str)
    assert format.lower() in ("pil", "opencv")


def convert(image, format="PIL"):
    cv2 = import_opencv()

    image_format_check(format)
    format = format.lower()

    # Image type is already correct - return image
    if any(
        [
            isinstance(image, Image.Image) and format == "pil",
            isinstance(image, ndarray) and format == "opencv",
        ]
    ):
        return image
    elif isinstance(image, Image.Image) and format == "opencv":
        # Convert PIL to OpenCV
        cv_image = asarray(image)
        if image.mode == "RGB":
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        return cv_image
    elif isinstance(image, ndarray) and format == "pil":
        # Convert OpenCV to PIL
        if len(image.shape) > 2 and image.shape[2] == 3:
            # If incoming image has 3 channels, convert from BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
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
