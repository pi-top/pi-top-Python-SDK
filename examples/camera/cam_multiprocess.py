from PyV4L2Camera.camera import Camera as V4L2Camera
from multiprocessing import Process, Event, RawArray
from ctypes import c_uint8
from PIL import Image
from pitop.core import ImageFunctions
import cv2
import numpy as np


def frame_producer(shared_array, e, w, h, d):
    _camera = V4L2Camera(f"/dev/video0", w, h)
    np_array = np.frombuffer(shared_array, np.uint8).reshape((h, w, d))
    while True:
        pil_image = Image.frombytes(
            'RGB',
            (w, h),
            _camera.get_frame(),
            'raw',
            'RGB'
        )
        np_array[:, :, :] = pil_image
        e.set()
        e.clear()


class Camera:
    def __init__(self, w, h, d):
        self.w, self.h, self.d = w, h, d
        self._shared_array = RawArray(c_uint8, h * w * d)
        self._new_frame_event = Event()
        self._process = Process(target=frame_producer, args=(self._shared_array, self._new_frame_event, w, h, d,))
        self._process.daemon = True
        self._process.start()


    def get_frame(self):
        self._new_frame_event.wait()
        array = np.frombuffer(self._shared_array, np.uint8).reshape((self.h, self.w, self.d))
        image = Image.fromarray(array)
        return image


if __name__ == "__main__":
    width = 640
    height = 480
    depth = 3
    camera = Camera(width, height, depth)
    while True:
        pil_frame = camera.get_frame()
        cv_frame = ImageFunctions.convert(pil_frame, "opencv")
        cv2.imshow("frame", cv_frame)
        cv2.waitKey(1)
