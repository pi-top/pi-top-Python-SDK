from concurrent.futures import ThreadPoolExecutor
from inspect import signature

from pitop.camera.pil_opencv_conversion import pil_to_opencv
from .capture_action_base import CaptureActionBase


class GenericAction(CaptureActionBase):
    """
    Class that executes the provided :data:`callback` whenever a camera frame
    is processed

    :param function callback_on_frame: A callback function that will be called with each new frame as the first argument.
    :param int frame_interval: The callback will run every frame_interval frames, decreasing the frame rate of processing.
    """

    def __init__(self, callback_on_frame, frame_interval, format='PIL'):
        self._generic_action_callback = callback_on_frame
        self._event_executor = ThreadPoolExecutor()
        self._frame_interval = frame_interval
        self._elapsed_frames = 0
        self._format = format

        callback_signature = signature(callback_on_frame)
        self.callback_has_argument = len(callback_signature.parameters) > 0

    def __del__(self):
        self.stop()

    def process(self, frame):
        if self._format.lower() == 'opencv':
            frame = pil_to_opencv(frame)

        if self._elapsed_frames % self._frame_interval == 0:
            if self.callback_has_argument:
                self._event_executor.submit(self._generic_action_callback, frame)
            else:
                self._event_executor.submit(self._generic_action_callback)
        self._elapsed_frames = (self._elapsed_frames + 1) % self._frame_interval

    def stop(self):
        if self._event_executor is not None:
            self._event_executor.shutdown()
            self._event_executor = None
