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

    def __init__(self, output_file_name="", fps=20.0, resolution=None):
        default_video_resolution = (640, 368)

        if output_file_name == "":
            output_directory = self._create_output_directory()
            output_file_name = self._get_output_filename(output_directory, "avi")

        if resolution is None:
            resolution = default_video_resolution

        def fix_dimension(dimension):
            if dimension % 16:
                dimension = dimension + 16 - dimension % 16
                PTLogger.warning(f"Invalid resolution. Setting dimension to {dimension}")
            return dimension

        self.__video_resolution = [fix_dimension(x) for x in resolution]
        self.__video_output_writer = get_writer(output_file_name,
                                                format="avi",
                                                mode="I",
                                                fps=fps)

    def process(self, frame):
        self.__video_output_writer.append_data(
            asarray(
                frame.resize(self.__video_resolution)
            )
        )

    def stop(self):
        if self.__video_output_writer is not None:
            self.__video_output_writer.close()
            self.__video_output_writer = None
