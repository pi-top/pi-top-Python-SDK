from imageio import get_writer
from numpy import asarray

from pitopcommon.logger import PTLogger

from .capture_action_base import CaptureActionBase


class VideoCapture(CaptureActionBase):
    """
    Class that stores camera frames as a video in the given :data:`output_file_name`.

    :param str output_file_name: The filename into which to write the video. If not provided, the file will
    be created in the directory ~/Camera/
    :param float fps: (Advanced) The framerate to use for the captured video. Defaults to 20.0 fps
    :param tuple resolution: (Advanced) The resolution to use for the captured video. Defaults to (640, 360)
    :param str codec: (Advanced) The codec to use for the captured video. Defaults to DIVX
    """

    _video_resolution = (640, 368)

    def __init__(self, output_file_name="", fps=20.0, resolution=None):
        if output_file_name == "":
            output_directory = self._create_output_directory()
            output_file_name = self._get_output_filename(output_directory, "avi")

        if resolution is None:
            resolution = self._video_resolution
        else:
            width = resolution[0]
            height = resolution[1]
            if width % 16:
                width = width + 16 - width % 16
                PTLogger.warning(f"Invalid resolution. Setting width to {width}")
            if height % 16:
                height = height + 16 - height % 16
                PTLogger.warning(f"Invalid resolution. Setting height to {height}")
            self._video_resolution = (width, height)

        self._video_output_writer = get_writer(output_file_name,
                                               format="avi",
                                               mode="I",
                                               fps=fps)

    def process(self, frame):
        frame = frame.resize(self._video_resolution)
        self._video_output_writer.append_data(asarray(frame))

    def stop(self):
        if self._video_output_writer is not None:
            self._video_output_writer.close()
            self._video_output_writer = None
