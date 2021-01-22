from os.path import isfile
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)


class Canvas:
    """
    The canvas class can be used to assemble complex images (e.g. a mix of images and text)
    and then render the entire image to the screen as a single frame.
    """

    def __init__(self, image, mode, size):
        # Image object to be used to draw to device
        self._image = image

        # Internal draw object derived from PIL image
        # Used by drawing functions - they directly affect the image
        self.__draw = ImageDraw.Draw(self._image)

        self.mode = mode
        self.size = size

        self.bounding_box = (0, 0, self.size[0] - 1, self.size[1] - 1)

        self.font_size = 30
        self.__font = None
        self.__font_path = None
        self.__init_font()

    ##################################################
    # Processing commands
    ##################################################
    def process_image(self, image_to_process):
        if image_to_process.size == self.size:
            image = image_to_process
            if image.mode != self.mode:
                image.convert(self.mode)
        else:
            # Size change will also handle mode change
            image = Image.new(
                self.mode,
                self.size,
                "black"
            )
            image.paste(
                image_to_process.resize(
                    self.size,
                    resample=self.resize_resampling_filter
                )
            )

        return image

    ##################################################
    # Rendering commands
    ##################################################

    def clear(self):
        """
        Clears the canvas.

        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.rectangle(self.bounding_box, 0)

    # TODO: add 'size' parameter for images being rendered to canvas
    # TODO: add 'fill', 'stretch', 'crop', etc. to OLED images - currently, they only stretch by default
    def image(self, xy, image):
        print("'image()' is now deprecated. Please use 'draw_image()'")
        self.draw_image(self, xy, image)

    def draw_image(self, xy, image):
        """
        Renders an image to the canvas at a given position.

        The image should be provided as a PIL Image object.

        Use the position methods in this class to specify the `xy`
        position parameter, e.g. `top_left`, `top_right`.

        :param tuple xy: The position on the canvas to render the image
        :param Image image: The image to render
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """

        self.__draw.bitmap(xy, self.process_image(image), 1)

    def text(self, xy, text, fill=1, spacing=0, align="left"):
        print("'text()' is now deprecated. Please use 'draw_text()'")
        self.draw_text(self, xy, text, fill=1, spacing=0, align="left")

    def draw_text(self, xy, text, fill=1, spacing=0, align="left"):
        """
        Draws a single line of text to the canvas.

        Use the position methods in this class to specify the `xy`
        position parameter, e.g. `top_left`, `top_right`.

        :param tuple xy: The position on the canvas to render the text
        :param string text: The string to render
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :param int spacing: The number of pixels between lines
        :param string align: Text alignment, `left`, `center` or `right`.
        :return: Current pixel map as 2D array
        """

        self.__draw.text(
            xy=xy,
            text=text,
            fill=fill,
            font=self.__check_for_and_get_font(),
            anchor=None,
            spacing=spacing,
            align=align,
        )

    def multiline_text(self, xy, text, fill=1, spacing=0, align="left"):
        print("'multiline_text()' is now deprecated. Please use 'draw_multiline_text()'")
        self.draw_multiline_text(self, xy, text, fill=1, spacing=0, align="left")

    def draw_multiline_text(self, xy, text, fill=1, spacing=0, align="left"):
        """
        Draws multi-line text to the canvas. Text that is too long for the screen
        will automatically wrap to the next line.

        Use the position methods in this class to specify the `xy`
        position parameter, e.g. `top_left`, `top_right`.

        :param tuple xy: The position on the canvas to render the text
        :param string text: The string to render
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :param int spacing: The number of pixels between lines
        :param string align: Text alignment, `left`, `center` or `right`.
        :return: Current pixel map as 2D array
        """

        def word_wrap(text):
            remaining = self.get_width()
            space_width, _ = self.textsize(" ")
            # use this list as a stack, push/popping each line
            output_text = []
            # split on whitespace...
            for word in text.split(None):
                word_width, _ = self.textsize(word)
                if word_width + space_width > remaining:
                    output_text.append(word)
                    remaining = self.get_width() - word_width
                else:
                    if not output_text:
                        output_text.append(word)
                    else:
                        output = output_text.pop()
                        output += " %s" % word
                        output_text.append(output)
                    remaining = remaining - (word_width + space_width)
            return "\n".join(output_text)

        text = word_wrap(text)

        self.__draw.multiline_text(
            xy=xy,
            text=text,
            fill=fill,
            font=self.__check_for_and_get_font(),
            anchor=None,
            spacing=spacing,
            align=align,
        )

    def arc(self, xy, start, end, fill=1):
        print("'arc()' is now deprecated. Please use 'draw_arc()'")
        self.draw_arc(self, xy, start, end, fill=1)

    def draw_arc(self, xy, start, end, fill=1):
        """
        Draws an arc (a portion of a circle outline) between the start and end angles, inside
        the given bounding box.

        :param tuple xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``.
        :param int start: Starting angle, in degrees. Angles are measured from
            3 o'clock, increasing clockwise.
        :param int end: Ending angle, in degrees.
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.arc(xy, start, end, fill)

    def chord(self, xy, start, end, fill=1, outline=1):
        print("'chord()' is now deprecated. Please use 'draw_chord()'")
        self.draw_chord(self, xy, start, end, fill=1, outline=1)

    def draw_chord(self, xy, start, end, fill=1, outline=1):
        """
        Same as arc(), but connects the end points with a straight line and
        can fill the enclosed space.

        :param tuple xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``
        :param int start: Starting angle, in degrees. Angles are measured from
            3 o'clock, increasing clockwise.
        :param int end: Ending angle, in degrees
        :param int fill: Color to use for the fill (1 pixel "on", 0 pixel "off")
        :param int outline: Color to use for the outline (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.chord(xy, start, end, fill, outline)

    def ellipse(self, xy, fill=1, outline=1):
        print("'ellipse()' is now deprecated. Please use 'draw_ellipse()'")
        self.draw_ellipse(self, xy, fill=1, outline=1)

    def draw_ellipse(self, xy, fill=1, outline=1):
        """
        Draws an ellipse inside the given bounding box.

        :param tuple xy: Four points to define the bounding box. Sequence of either
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``
        :param int fill: Color to use for the fill (1 pixel "on", 0 pixel "off")
        :param int outline: Color to use for the outline (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.ellipse(xy, fill, outline)

    def line(self, xy, fill=1, width=1):
        print("'line()' is now deprecated. Please use 'draw_line()'")
        self.draw_line(self, xy, fill=1, width=1)

    def draw_line(self, xy, fill=1, width=1):
        """
        Draws a line between the coordinates in the **xy** list.

        :param tuple xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
            numeric values like ``[x, y, x, y, ...]``
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :param width: The line width, in pixels
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.line(xy, fill, width)

    def pieslice(self, xy, start, end, fill=1, outline=1):
        print("'pieslice()' is now deprecated. Please use 'draw_pieslice()'")
        self.draw_pieslice(self, xy, start, end, fill=1, outline=1)

    def draw_pieslice(self, xy, start, end, fill=1, outline=1):
        """
        Same as arc, but also draws straight lines between the end points and the
        center of the bounding box.

        :param tuple xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``
        :param int start: Starting angle, in degrees. Angles are measured from
            3 o'clock, increasing clockwise.
        :param int end: Ending angle, in degrees
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :param int outline: Color to use for the outline (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.pieslice(xy, start, end, fill, outline)

    def point(self, xy, fill=1):
        print("'point()' is now deprecated. Please use 'draw_point()'")
        self.draw_point(self, xy, fill=1)

    def draw_point(self, xy, fill=1):
        """
        Draws points (individual pixels) at the given coordinates.

        :param tuple xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
            numeric values like ``[x, y, x, y, ...]``
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.point(xy, fill)

    def polygon(self, xy, fill=1):
        print("'polygon()' is now deprecated. Please use 'draw_polygon()'")
        self.draw_polygon(self, xy, fill=1)

    def draw_polygon(self, xy, fill=1):
        """
        Draws a polygon.

        The polygon outline consists of straight lines between the given
        coordinates, plus a straight line between the last and the first
        coordinate.

        :param tuple xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
            numeric values like ``[x, y, x, y, ...]``
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.polygon(xy, fill)

    def rectangle(self, xy, fill=1):
        print("'rectangle()' is now deprecated. Please use 'draw_rectangle()'")
        self.draw_rectangle(self, xy, fill=1)

    def draw_rectangle(self, xy, fill=1):
        """
        Draws a rectangle.

        :param tuple xy: Four points to define the bounding box. Sequence of either
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``. The second point
            is just outside the drawn rectangle.
        :param int fill: Color to use (1 pixel "on", 0 pixel "off")
        :return: The current canvas pixel map as a 2D array
        :rtype: array
        """
        self.__draw.rectangle(xy, fill)

    ##################################################
    # Position/dimension methods
    ##################################################

    def get_bounding_box(self):
        """
        Gets the bounding rectangle of the pi-top OLED display as a tuple.

        :return: A tuple containing the bounding rectangle of the canvas
        :rtype: tuple
        """
        return self.bounding_box

    def __get_corner(self, pos1, pos2):
        """
        Gets corner of bounding box.

        :return: coordinates of the corner
        :rtype: tuple
        """
        return (
            self.bounding_box[pos1],
            self.bounding_box[pos2]
        )

    def top_left(self):
        """
        Gets the top left corner of the pi-top OLED display.

        :return: The top-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 1)

    def top_right(self):
        """
        Gets the top-right corner of the pi-top OLED display.

        :return: The top-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(2, 1)

    def bottom_left(self):
        """
        Gets the bottom-left corner of the pi-top OLED display.

        :return: The bottom-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(0, 3)

    def bottom_right(self):
        """
        Gets the bottom-right corner of the pi-top OLED display.

        :return: The bottom-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.__get_corner(2, 3)

    def get_size(self):
        """
        Gets the dimensions of the pi-top OLED display

        :return: The dimensions of the canvas as a tuple
        :rtype: tuple
        """
        return self.size

    def get_width(self):
        """
        Gets the width of the  pi-top OLED display

        :return: The width of canvas in pixels
        :rtype: int
        """
        return self.size[0]

    def get_height(self):
        """
        Gets the height of the pi-top OLED display

        :return: The height of canvas in pixels
        :rtype: int
        """
        return self.size[1]

    ##################################################
    # Font config methods
    ##################################################

    def __update_font(self):
        """
        Updates font
        """
        if self.__font_path is None:
            raise Exception(
                "No font path set - call set_font_path(font_path)"
            )
        self.__font = ImageFont.truetype(self.__font_path, size=self.font_size)

    def __check_for_and_get_font(self):
        """
        Checks if the font is set. if the font is not set raise exception.
        :return: font or raise exception if _font = None
        """
        if self.__font is None:
            raise Exception(
                "No font set - call set_font_path(font_path) before using text functions"
            )
        return self.__font

    def __init_font(self):
        """
        Initialize font to primary or fall back font.
        """
        primary_font_path = "/usr/share/fonts/opentype/FSMePro/FSMePro-Light.otf"
        fallback_font_path = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

        if isfile(primary_font_path):
            self.set_font(primary_font_path, self.font_size)
        elif isfile(fallback_font_path):
            self.set_font(fallback_font_path, self.font_size)

    def get_font_path(self):
        """
        Gets the path of the current font used for rendering text to the canvas.

        :return: The path to the font file
        :rtype: string
        """
        return self.__font_path

    def set_font_path(self, font_path):
        """
        Sets the path of the current font used for rendering text to the canvas.

        :param string font_path: The font file to use for text rendering
        """
        self.set_font(font_path)

    def set_font(self, font_path, font_size=None):
        """
        Sets the font and pixel size used for rendering text to the canvas.

        :param string font_path: The path to the font file
        :param int font_size: The font size to use
        """
        self.__font_path = font_path
        if font_size is not None:
            self.font_size = font_size
        self.__update_font()

    def get_font_size(self):
        """
        Gets the current font size used for rendering text to the canvas.

        :return: The current font size
        :rtype: int
        """
        return self.font_size

    def set_font_size(self, font_size):
        """
        Gets the current font size used for rendering text to the canvas.

        :param int font_size: The font size to use
        """
        self.font_size = font_size
        self.__update_font()

    def textsize(self, text, spacing=4):
        """
        Return the size of the given string, in pixels, as it would be rendered
        to the canvas.

        :param string text:  Text to be measured. If it contains any newline
            characters, the text is passed on to multiline_textsize()
        :param int spacing: The number of pixels between lines
        :return: int
        """

        return self.__draw.textsize(
            text=text, font=self.__check_for_and_get_font(), spacing=spacing
        )

    def multiline_textsize(self, text, spacing=4):
        """
        Return the size of the given string, in pixels, as it would be rendered
        to the canvas.

        :param string text:  Text to be measured. If it contains any newline
            characters, the text is passed on to multiline_textsize()
        :param int spacing: The number of pixels between lines
        :return: int
        """

        return self.__draw.multiline_textsize(
            text=text, font=self.__check_for_and_get_font(), spacing=spacing
        )
