import numpy as np


def pil_to_opencv(image):
    return np.array(image)[:, :, ::-1]
