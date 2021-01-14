from PIL import Image
from urllib.request import urlopen

from pitopcommon.formatting import is_url


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


def process_pil_image_frame(pil_image, size, mode):
    staging_data = Image.new("RGB", size, "black")
    staging_data.paste(pil_image.resize(size))

    image_data = staging_data.convert(mode)

    return image_data
