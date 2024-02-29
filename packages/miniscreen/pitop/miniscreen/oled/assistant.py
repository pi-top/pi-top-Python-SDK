import PIL.Image
import PIL.ImageChops
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
import PIL.ImageSequence


class Fonts:
    _roboto_directory = ""
    _vera_directory = ""

    @staticmethod
    def regular():
        return f"{Fonts._roboto_directory}Roboto-Regular.ttf"

    @staticmethod
    def mono(bold, italics):
        if bold and not italics:
            return f"{Fonts._vera_directory}VeraMoBd.ttf"
        if not bold and italics:
            return f"{Fonts._vera_directory}VeraMoIt.ttf"
        if bold and italics:
            return f"{Fonts._vera_directory}VeraMoBI.ttf"
        return f"{Fonts._vera_directory}VeraMono.ttf"


class MiniscreenAssistant:
    resize_resampling_filter = PIL.Image.NEAREST

    def __init__(self, mode, size):
        self.image_mode = mode
        self.image_size = size

    @property
    def _width(self):
        return self.image_size[0]

    def get_frame_iterator(self, image):
        return PIL.ImageSequence.Iterator(image)

    def images_match(self, image1, image2):
        return PIL.ImageChops.difference(image1, image2).getbbox() is None

    def clear(self, image):
        PIL.ImageDraw.Draw(image).rectangle(((0, 0), image.size), fill=0)

    def invert(self, image):
        return PIL.ImageOps.invert(image.convert("L")).convert("1")

    def _multiline_split(self, text, font, font_size, spacing):
        def get_text_size(text):
            return PIL.ImageDraw.Draw(self.empty_image).textsize(
                text=str(text),
                font=PIL.ImageFont.truetype(font, size=font_size),
                spacing=spacing,
            )

        remaining = self._width
        space_width, _ = get_text_size(" ")
        # use this list as a stack, push/popping each line
        output_text = []
        # split on whitespace...
        for word in text.split(None):
            word_width, _ = get_text_size(word)
            if word_width + space_width > remaining:
                output_text.append(word)
                remaining = self._width - word_width
            else:
                if not output_text:
                    output_text.append(word)
                else:
                    output = output_text.pop()
                    output += " %s" % word
                    output_text.append(output)
                remaining = remaining - (word_width + space_width)
        return "\n".join(output_text)

    def render_text(
        self,
        image,
        text,
        wrap=True,
        xy=None,
        font_size=None,
        font=None,
        align=None,
        anchor=None,
        fill=1,
        spacing=0,
    ):
        if type(image) is PIL.Image.Image:
            draw = PIL.ImageDraw.Draw(image)
        else:
            draw = image

        if xy is None:
            xy = self.get_recommended_text_pos()

        if font_size is None:
            font_size = self.get_recommended_font_size()

        if font is None:
            font = self.get_recommended_font_path(font_size)

        if align is None:
            align = self.get_recommended_text_align()

        if anchor is None:
            anchor = self.get_recommended_text_anchor()

        if wrap:
            text = self._multiline_split(text, font, font_size, spacing)
            cmd = draw.text
        else:
            cmd = draw.multiline_text

        cmd(
            xy,
            str(text),
            font=PIL.ImageFont.truetype(font, size=font_size),
            fill=fill,
            spacing=spacing,
            align=align,
            anchor=anchor,
        )

    def process_image(self, image_to_process):
        if image_to_process.size == self.image_size:
            image = image_to_process
            if image.mode != self.image_mode:
                image = image.convert(self.image_mode)
        else:
            image = PIL.Image.new(self.image_mode, self.image_size, "black")
            image.paste(
                image_to_process.resize(
                    self.image_size, resample=self.resize_resampling_filter
                )
            )

        return image

    def get_recommended_text_pos(self):
        # Center of display
        return tuple(x / 2 for x in self.image_size)

    def get_recommended_text_anchor(self):
        # Centered text
        return "mm"

    def get_recommended_text_align(self):
        # Centered text
        return "center"

    def get_recommended_font_size(self):
        return 14

    def get_recommended_font(self, size=None):
        if size is None:
            size = self.get_recommended_font_size()
        return PIL.ImageFont.truetype(self.get_recommended_font_path(size), size=size)

    def get_recommended_font_path(self, size=None):
        if size is None:
            size = self.get_recommended_font_size()
        font_path = self.get_regular_font_path()
        if size < 12:
            font_path = self.get_mono_font_path()

        return font_path

    def get_regular_font(self, size=None):
        if size is None:
            size = self.get_recommended_font_size()
        return PIL.ImageFont.truetype(self.get_regular_font_path(), size=size)

    def get_regular_font_path(self):
        return Fonts.regular()

    def get_mono_font(self, size=11, bold=False, italics=False):
        if size is None:
            size = self.get_recommended_font_size()
        return PIL.ImageFont.truetype(self.get_mono_font_path(bold, italics), size=size)

    def get_mono_font_path(self, bold=False, italics=False):
        return Fonts.mono(bold, italics)

    @property
    def empty_image(self):
        return PIL.Image.new(self.image_mode, self.image_size, "black")

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

        :return: The top-left coordinates of the canvas bounding box as
            a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 1)

    def top_right(self):
        """Gets the top-right corner of the pi-top OLED display.

        :return: The top-right coordinates of the canvas bounding box as
            a tuple
        :rtype: tuple
        """
        return self.__get_corner(2, 1)

    def bottom_left(self):
        """Gets the bottom-left corner of the pi-top OLED display.

        :return: The bottom-left coordinates of the canvas bounding box
            as a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 3)

    def bottom_right(self):
        """Gets the bottom-right corner of the pi-top OLED display.

        :return: The bottom-right coordinates of the canvas bounding box
            as a tuple
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
