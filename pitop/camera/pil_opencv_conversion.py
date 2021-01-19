import numpy as np
from PIL import Image


# For RGB - BGR conversion we can reverse the third level of the pixels ndarray
# That is what [:, :, ::-1] does - https://stackoverflow.com/a/14140796

def pil_to_opencv(image):
    """
    Converts an RGB Pillow Image into an OpenCV compatible BGR numpy ndarray.

    :type image: PIL.Image.Image
    :param image: A Pillow Image instance in raw RGB format
    :rtype: numpy.ndarray
    :return:
        A numpy array representing the image in BGR format, as used by default in OpenCV
    """
    return np.array(image)[:, :, ::-1]


def opencv_to_pil(image):
    """
    Converts an OpenCV compatible BGR numpy ndarray into an RGB Pillow Image.

    :type image: numpy.ndarray
    :param image: Raw BGR image data as a numpy ndarray
    :rtype: PIL.Image.Image
    :return:
        A Pillow Image in RGB format
    """
    if len(image.shape) == 3:
        return Image.fromarray(image[:, :, ::-1])
    else:
        return Image.fromarray(image[:, :])
