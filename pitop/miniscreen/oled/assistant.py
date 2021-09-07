from PIL import Image, ImageFont


class MiniscreenAssistant:
    resize_resampling_filter = Image.NEAREST

    def __init__(self, mode, size):
        self.image_mode = mode
        self.image_size = size

    def process_image(self, image_to_process):
        if image_to_process.size == self.image_size:
            image = image_to_process
            if image.mode != self.image_mode:
                image = image.convert(self.image_mode)
        else:
            image = Image.new(self.image_mode, self.image_size, "black")
            image.paste(
                image_to_process.resize(
                    self.image_size, resample=self.resize_resampling_filter
                )
            )

        return image

    def get_recommended_text_pos(self):
        return self.top_left()

    def get_recommended_font_size(self):
        return 30

    def get_recommended_font(self, size=15):
        return ImageFont.truetype(self.get_recommended_font_path(size), size=size)

    def get_recommended_font_path(self, size=15):
        font_path = self.get_regular_font_path()
        if size < 12:
            font_path = self.get_mono_font()

        return font_path

    def get_regular_font(self, size=15):
        return ImageFont.truetype(self.get_regular_font_path(), size=size)

    def get_regular_font_path(self, size=15):
        return "Roboto-Regular.ttf"

    def get_mono_font(self, size=11):
        return ImageFont.truetype(self.get_mono_font_path(), size=size)

    def get_mono_font_path(self, size=11):
        return "VeraMono.ttf"

    @property
    def empty_image(self):
        return Image.new(self.image_mode, self.image_size, "black")

    @property
    def bounding_box(self):
        return (0, 0, self.image_size[0] - 1, self.image_size[1] - 1)

    def get_bounding_box(self):
        """Gets the bounding rectangle of the pi-top OLED display as a tuple.

        :return: A tuple containing the bounding rectangle of the canvas
        :rtype: tuple
        """
        return self.bounding_box

    def __get_corner(self, pos1, pos2):
        """Gets corner of bounding box.

        :return: coordinates of the corner
        :rtype: tuple
        """
        return (self.bounding_box[pos1], self.bounding_box[pos2])

    def top_left(self):
        """Gets the top left corner of the pi-top OLED display.

        :return: The top-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 1)

    def top_right(self):
        """Gets the top-right corner of the pi-top OLED display.

        :return: The top-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(2, 1)

    def bottom_left(self):
        """Gets the bottom-left corner of the pi-top OLED display.

        :return: The bottom-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 3)

    def bottom_right(self):
        """Gets the bottom-right corner of the pi-top OLED display.

        :return: The bottom-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(2, 3)

    def get_size(self):
        """Gets the dimensions of the pi-top OLED display.

        :return: The dimensions of the canvas as a tuple
        :rtype: tuple
        """
        return self.image_size

    def get_width(self):
        """Gets the width of the  pi-top OLED display.

        :return: The width of canvas in pixels
        :rtype: int
        """
        return self.image_size[0]

    def get_height(self):
        """Gets the height of the pi-top OLED display.

        :return: The height of canvas in pixels
        :rtype: int
        """
        return self.image_size[1]
