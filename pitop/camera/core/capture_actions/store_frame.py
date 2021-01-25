from .capture_action_base import CaptureActionBase


class StoreFrame(CaptureActionBase):
    """
    Class used to store a frame into :data:`output_file_name` when :data:`process` is called
    """

    def __init__(self, output_file_name=""):
        if output_file_name == "":
            output_directory = self._create_output_directory()
            output_file_name = self._get_output_filename(output_directory, "png")
        self.__output_file_name = output_file_name

    def process(self, frame):
        if hasattr(frame, "save"):
            frame.save(self.__output_file_name)

    def stop(self):
        pass
