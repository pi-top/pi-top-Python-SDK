from PIL import Image, ImageSequence
import re
import urllib.request


# TODO: move to common library
url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class OLEDImage:
    """
    The OLEDImage class is used for rendering static images and animations to
    the pi-top [4] OLED.
    """

    def __init__(self, file_path_or_url, loop=False):
        """
        :param string file_path_or_url: The image file path or URL
        """
        is_url = re.match(url_regex, file_path_or_url) is not None
        self._image = Image.open(urllib.request.urlopen(
            file_path_or_url) if is_url else file_path_or_url)
        self.loop = loop

        self.frame_no = 0

        if self.is_animated:
            self.max_frame_no = self._image.n_frames - 1
            self._frames_of_image = ImageSequence.Iterator(self._image)
        else:
            self.max_frame_no = 0

        self.finished = not self.is_animated

    @property
    def is_animated(self):
        """
        Indicates whether the image encapsulated by the class is animated.

        :return: Whether the image is animated
        :rtype: bool
        """
        try:
            return self._image.is_animated
        except AttributeError:
            return False

    def data(self, oled_device):
        """
        Gets the raw image data (for the current frame, if the image is
        animated)

        :return: The raw image data for drawing to screen
        :rtype: Image
        """

        frame = self._frames_of_image[self.frame_no]
        image = Image.new("RGB", oled_device.size, "black")
        image.paste(frame.resize(oled_device.size))

        return image.convert(oled_device.mode)

    def __update_frame(self, frame_no):
        self.frame_no = frame_no

    def next_frame(self):
        """
        Moves the animation to the next frame
        """
        if self.is_animated and not self.finished:

            if self.frame_no < self.max_frame_no:
                self.__update_frame(self.frame_no + 1)

            elif self.loop:
                self.__update_frame(0)

            else:
                self.finished = True
