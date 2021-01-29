from PIL import Image
from numpy import array
from urllib.request import urlopen

from pitopcommon.formatting import is_url


def __image_has_3_channels(image: array):
    # RGB
    return len(image.shape) == 3


def __image_rgb_bgr_convert(image: array):
    # For RGB - BGR conversion we can reverse the third level of the pixels ndarray
    # https://stackoverflow.com/a/14140796
    return image[:, :, ::-1]


def pil_to_opencv(image: Image):
    """
    Converts an RGB Pillow Image into an OpenCV compatible BGR numpy ndarray.

    :type image: PIL.Image.Image
    :param image: A Pillow Image instance in raw RGB format
    :rtype: numpy.ndarray
    :return:
        A numpy array representing the image in BGR format, as used by default in OpenCV
    """
    image = array(image)

    if __image_has_3_channels(image):
        # Array has 3 channel, do nothing
        image = __image_rgb_bgr_convert(image)
    else:
        image = image

    return image


def opencv_to_pil(image: array):
    """
    Converts an OpenCV compatible BGR numpy ndarray into an RGB Pillow Image.

    :type image: numpy.ndarray
    :param image: Raw BGR image data as a numpy ndarray
    :rtype: PIL.Image.Image
    :return:
        A Pillow Image in RGB format
    """
    image = array(image)
    if __image_has_3_channels(image):
        image = Image.fromarray(__image_rgb_bgr_convert(image))
    else:
        # Not 3 channel, do nothing
        image = Image.fromarray(image)

    return image


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
