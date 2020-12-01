from PIL import Image

from pitopcommon.formatting import is_url

from urllib import urllib


def get_pil_image_from_path(file_path_or_url):
    if is_url(file_path_or_url):
        image_path = urllib.request.urlopen(file_path_or_url)
    else:
        image_path = file_path_or_url

    image = Image.open(image_path)
    image.verify()
    # Need to close and re-open after verifying...
    image.close()
    image = Image.open(image_path)
    return image


def process_pil_image(pil_image, size, mode):
    staging_data = Image.new("RGB", size, "black")
    staging_data.paste(pil_image.resize(size))

    image_data = staging_data.convert(mode)

    return image_data
