from PyV4L2Camera.camera import Camera as V4L2Camera
from multiprocessing import Process, Event, RawArray
from ctypes import c_uint8
from PIL import Image
from pitop.core import ImageFunctions
import cv2
import numpy as np
from threading import Thread
from threading import Event as TheadEvent
from time import sleep
from pitop import UltrasonicSensor


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
        self._processing_frame_event = Event()
        self._process = Process(target=frame_producer, args=(self._shared_array, self._processing_frame_event, w, h, d,))
        self._process.daemon = True
        self._process.start()

        self._frame = None
        self.on_frame = None
        self._threading_event = TheadEvent()
        self._process_frame_thread = Thread(target=self.__process_frame, daemon=True)
        self._process_frame_thread.start()

    def __get_frame_from_multiprocessing(self):
        self._processing_frame_event.wait()
        array = np.frombuffer(self._shared_array, np.uint8).reshape((self.h, self.w, self.d))
        frame = Image.fromarray(array)
        return frame

    def __process_frame(self):
        while True:
            self._frame = self.__get_frame_from_multiprocessing()
            self._threading_event.set()
            self._threading_event.clear()

            if callable(self.on_frame):
                self.on_frame(self._frame)

    def get_frame(self):
        self._threading_event.wait()
        return self._frame


if __name__ == "__main__":
    def view_frame_cv(frame, title):
        cv_frame = ImageFunctions.convert(frame, "opencv")
        cv2.imshow(title, cv_frame)
        cv2.waitKey(1)

    def callback(frame):
        view_frame_cv(frame, "on_frame mode")

    width = 640
    height = 480
    depth = 3

    camera = Camera(width, height, depth)

    print("Testing ultrasonic")
    ultrasonic = UltrasonicSensor("D3")
    for _ in range(100):
        print(f"distance: {ultrasonic.distance}")
        sleep(0.1)

    print("Running get frame mode")
    for _ in range(150):
        pil_frame = camera.get_frame()
        view_frame_cv(pil_frame, "get_frame mode")

    print("Running on_frame callback mode")
    camera.on_frame = callback
    sleep(5)
    cv2.destroyAllWindows()
