from os import mkdir, path
from time import strftime
from pathlib import Path
from abc import ABC, abstractmethod


class CaptureActionBase(ABC):
    """
    Abstract class from which all capture actions classes must inherit from.
    """

    @abstractmethod
    def process(self, frame):
        pass

    @abstractmethod
    def stop(self):
        pass

    def _get_output_filename(self, directory, extension):
        return path.join(directory, "output_" + strftime("%Y-%m-%d-%H-%M-%S") + "." + extension)

    def _create_output_directory(self):
        output_directory = path.join(str(Path.home()), "Camera")

        if not path.isdir(output_directory):
            mkdir(output_directory)

        return output_directory
