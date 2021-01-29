from .capture_action_base import CaptureActionBase

from pitop.core import ImageFunctions

from concurrent.futures import ThreadPoolExecutor
from inspect import signature


class GenericAction(CaptureActionBase):
    """
    Class that executes the provided :data:`callback` whenever a camera frame
    is processed

    :param function callback_on_frame: A callback function that will be called with each new frame as the first argument.
    :param int frame_interval: The callback will run every frame_interval frames, decreasing the frame rate of processing.
    """

    def __init__(self, callback_on_frame, frame_interval, format='PIL'):
        self.__generic_action_callback = callback_on_frame
        self.__event_executor = ThreadPoolExecutor()
        self.__frame_interval = frame_interval
        self.__elapsed_frames = 0
        self.__format = format

        callback_signature = signature(callback_on_frame)
        self.callback_has_argument = len(callback_signature.parameters) > 0

    def __del__(self):
        self.stop()

    def process(self, frame):
        if isinstance(self.__format, str) and self.__format.lower() == 'opencv':
            frame = ImageFunctions.pil_to_opencv(frame)

        if self.__elapsed_frames % self.__frame_interval == 0:
            if self.callback_has_argument:
                self.__event_executor.submit(self.__generic_action_callback, frame)
            else:
                self.__event_executor.submit(self.__generic_action_callback)
        self.__elapsed_frames = (self.__elapsed_frames + 1) % self.__frame_interval

    def stop(self):
        if self.__event_executor is not None:
            self.__event_executor.shutdown()
            self.__event_executor = None
