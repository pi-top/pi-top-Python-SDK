from pitop.core import ImageFunctions
import os


class FsImage:
    def __init__(self, path: str):
        self.path = path
        self.data = ImageFunctions.get_pil_image_from_path(self.path)
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
        self.__images_arr = []
        self.__current_index = 0
        self.__current_image = None

        self.__file_starts_with = file_starts_with
        self.__file_ends_with = file_ends_with

        self.__load_images()
        self.__load_frame(self.__current_index)

    def __load_images(self, starts_with: str = "", ends_with: str = ""):
        self.__images_arr = []

        with os.scandir(self.path) as it:
            for file_path in it:
                if not(file_path.name.startswith(self.__file_starts_with) or file_path.name.endswith(self.__file_ends_with)):
                    continue

                try:
                    image_obj = FsImage(file_path.path)
                    self.__images_arr.append(image_obj)
                except Exception:
                    continue

    def reset(self):
        self.__current_index = 0
        self.__load_frame(self.__current_index)

    def __advance(self):
        index = min(self.__current_index + 1, len(self.__images_arr) - 1)
        if index == self.__current_index:
            return

        self.__current_index = index
        self.__load_frame(self.__current_index)

    def __load_frame(self, index: int):
        if 0 <= index < len(self.__images_arr):
            self.__current_image = self.__images_arr[index]

    def current_frame_source(self):
        return self.__current_image.path

    def is_opened(self):
        return self.__current_image is not None

    def get_frame(self):
        self.__advance()
        return self.__current_image.data
