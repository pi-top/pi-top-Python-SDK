import os
from PIL import Image


class FsImage:
    def __init__(self, path: str):
        self.path = path
        self.data = Image.open(self.path)
        if self.data is None:
            raise AttributeError(f"Couldn't load image {path}")


class FileSystemCamera:
    """
    Class that mocks the behaviour of a camera, by using a set of pictures from the given :data:`path`

    :param str path: path where images to be used by the camera are located in the system
    :param str file_starts_with: filter images from the given path to use only the ones that start with the given string
    :param str file_ends_with: filter images from the given path to use only the ones that end with the given string
    """

    def __init__(self, path: str = "/tmp", file_starts_with: str = "", file_ends_with: str = ""):
        if not os.path.isdir(path):
            raise FileExistsError(f"Provided path {path} doesn't exist")

        self.path = path
        self._images_arr = []
        self._current_index = 0
        self._current_image = None

        self.__file_starts_with = file_starts_with
        self.__file_ends_with = file_ends_with

        self._load_images()
        self._load_frame(self._current_index)

    def _load_images(self, starts_with: str = "", ends_with: str = ""):
        self._images_arr = []

        with os.scandir(self.path) as it:
            for file_path in it:
                if not(file_path.name.startswith(self.__file_starts_with) or file_path.name.endswith(self.__file_ends_with)):
                    continue

                try:
                    image_obj = FsImage(file_path.path)
                    self._images_arr.append(image_obj)
                except Exception:
                    continue

    def reset(self):
        self._current_index = 0
        self._load_frame(self._current_index)

    def _advance(self):
        index = min(self._current_index + 1, len(self._images_arr) - 1)
        if index == self._current_index:
            return

        self._current_index = index
        self._load_frame(self._current_index)

    def _load_frame(self, index: int):
        if 0 <= index < len(self._images_arr):
            self._current_image = self._images_arr[index]

    def current_frame_source(self):
        return self._current_image.path

    def is_opened(self):
        return self._current_image is not None

    def get_frame(self):
        self._advance()
        return self._current_image.data
