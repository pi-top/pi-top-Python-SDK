import numpy as np


def pil_to_opencv(image):
    """
    Converts an RGB Pillow Image into an OpenCV compatible BGR numpy ndarray.

    :type image: PIL.Image.Image
    :param image: A Pillow Image instance in raw RGB format
    :rtype: numpy.ndarray
    :return:
        A numpy array representing the image in BGR format, as used by default in OpenCV
    """
    # RGB to BGR - reverse the third level arrays https://stackoverflow.com/a/14140796
    return np.array(image)[:, :, ::-1]
