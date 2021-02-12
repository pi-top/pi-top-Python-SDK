from numpy import (
    asarray,
    ndarray,
)
from PIL import Image, ImageDraw
from re import split
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


def get_word_wrapped_text_for_image(text, font, xy, image):
    max_width = image.width - xy[0]

    # Push and pop each line to stack
    output_text = list()

    remaining = max_width

    # Split up text based on all whitespace
    for field in split(r'(\s+)', text):
        # Get text size
        field_width, field_height = ImageDraw.Draw(image).textsize(
            text=str(field),
            font=font,
            spacing=0,
        )
        if field_width > remaining:
            # Update remaining width
            remaining = max_width - field_width

            # Not enough space to add to current line - start new one
            output_text.append(field)
        else:
            # Update remaining width
            remaining = remaining - field_width

            # Is enough space
            if not output_text:
                # First time - just append
                output_text.append(field)
            else:
                # Pop latest line from list
                # Append the field with a space
                # Add back to list
                output_text.append(output_text.pop() + f" {field}")

    return "\n".join(output_text)
