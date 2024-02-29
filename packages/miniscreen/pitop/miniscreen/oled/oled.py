import logging
from atexit import register
from threading import Thread, current_thread, main_thread
from time import sleep

from pitop.common.ptdm import Message, PTDMSubscribeClient
from pitop.core import ImageFunctions

from .assistant import MiniscreenAssistant
from .core import FPS_Regulator, OledDeviceController

logger = logging.getLogger(__name__)


class OLED:
    """Provides access to the miniscreen display on the pi-top [4], and exposes
    methods for simple rendering of text or images to the screen."""

    def __init__(self):
        self._controller = OledDeviceController(self._redraw_last_image)

        self.assistant = MiniscreenAssistant(self.mode, self.size)

        self.image = self.assistant.empty_image
        self._image = self.assistant.empty_image

        self.__fps_regulator = FPS_Regulator()

        self.__visible = False
        self.__auto_play_thread = None

        self.reset()

        def reset_miniscreen() -> None:
            logger.debug("pi-topd is ready - resetting miniscreen")
            try:
                backup_image = self.image
                self.reset()
                self.display_image(backup_image)
            except RuntimeError as e:
                logger.error(f"Error resetting miniscreen: {e}")
                raise Exception(
                    "Error resetting miniscreen. Please re-create the Miniscreen object"
                )

        self._ptdm_subscribe_client = PTDMSubscribeClient()
        self._ptdm_subscribe_client.initialise(
            {Message.PUB_PITOPD_READY: reset_miniscreen}
        )
        self._ptdm_subscribe_client.start_listening()

        register(self.__cleanup)

    def prepare_image(self, image_to_prepare):
        """Formats the given image into one that can be used directly by the
        OLED.

        :type image_to_prepare: :class:`PIL.Image.Image`
        :param image_to_prepare: Image to be formatted.
        :rtype: :class:`PIL.Image.Image`
        """
        # TODO: deprecate this function in favour of user handling this directly
        return self.assistant.process_image(image_to_prepare)

    def should_redisplay(self, image_to_display=None):
        """Determines if the miniscreen display needs to be refreshed, based on
        the provided image. If no image is provided, the content of the
        display's deprecated internal canvas property will be used.

        :type image_to_display: :class:`PIL.Image.Image` or None
        :param image_to_display: Image to be displayed.
        :rtype: bool
        """
        # Use canvas image if no image is offered
        if image_to_display is None:
            image_to_display = self._image

        return self.image is None or not self.assistant.images_match(
            self.image, image_to_display
        )

    @property
    def spi_bus(self):
        """Gets the SPI bus used by the miniscreen display to receive data as
        an integer. Setting this property will modify the SPI bus that the OLED
        uses. You might notice a flicker in the screen.

        :param int bus: Number of the SPI bus for the OLED to use. Accepted values are `0` or `1`.
        """
        return self._controller.spi_bus

    @spi_bus.setter
    def spi_bus(self, bus):
        assert bus in (0, 1)
        self._controller.spi_bus = bus

    @property
    def device(self):
        """Gets the miniscreen display device instance.

        :rtype: :class:`pitop.miniscreen.oled.core.contrib.luma.oled.device.sh1106`
        """
        return self._controller.get_device()

    @property
    def size(self):
        """Gets the size of the miniscreen display as a (width, height) tuple.

        :rtype: tuple
        """
        return self.device.size

    @property
    def width(self):
        """Gets the width of the miniscreen display.

        :rtype: int
        """
        return self.size[0]

    @property
    def height(self):
        """Gets the height of the miniscreen display.

        :rtype: int
        """
        return self.size[1]

    @property
    def mode(self):
        return self.device.mode

    @property
    def visible(self):
        """Gets whether the device is currently in low power state.

        :return: whether the screen is in low power mode
        :rtype: bool
        """
        return not self.__visible

    def set_control_to_pi(self):
        """Signals the pi-top hub to give control of the miniscreen display to
        the Raspberry Pi."""
        self._controller.set_control_to_pi()

    def set_control_to_hub(self):
        """Signals the pi-top hub to take control of the miniscreen display."""
        self._controller.set_control_to_hub()

    def set_max_fps(self, max_fps):
        """Set the maximum frames per second that the miniscreen display can
        display. This method can be useful to control or limit the speed of
        animations.

        This works by blocking on the OLED's display methods if called
        before the amount of time that a frame should last is not
        exceeded.

        :param int max_fps: The maximum frames that can be rendered per
            second
        """
        self.__fps_regulator.set_max_fps(max_fps)

    def show(self):
        """The miniscreen display comes out of low power mode showing the
        previous image shown before hide() was called (so long as display() has
        not been called)"""
        self.device.show()
        self.__visible = True

    def hide(self):
        """The miniscreen display is put into low power mode.

        The previously shown image will re-appear when show() is given,
        even if the internal frame buffer has been changed (so long as
        display() has not been called).
        """
        self.device.hide()
        self.__visible = False

    def contrast(self, new_contrast_value):
        """Sets the contrast value of the miniscreen display to the provided
        value.

        :param int new_contrast_value: contrast value to set, between 0
            and 255.
        """
        assert new_contrast_value in range(0, 256)

        self.device.contrast(new_contrast_value)

    def wake(self):
        """The miniscreen display is set to high contrast mode, without
        modifying the content of the screen."""
        self.contrast(255)

    def sleep(self):
        """The miniscreen display in set to low contrast mode, without
        modifying the content of the screen."""
        self.contrast(0)

    def clear(self):
        """Clears any content displayed in the miniscreen display."""
        self.assistant.clear(self._image)
        self.__display(self._image, force=True)

    # TODO: evaluate dropping this 'redraw last image' function at v1.0.0
    #
    # this is only necessary to support users with SPI0 on device
    # with older SDK version that only supported SPI1
    def _redraw_last_image(self):
        if hasattr(self, "image"):
            self.__display(self.image, force=True)

    def refresh(self):
        self.set_control_to_pi()
        self._controller.reset_device()
        self._redraw_last_image()

    def reset(self, force=True):
        """Gives the caller access to the miniscreen display (i.e. in the case
        the system is currently rendering information to the screen) and clears
        the screen."""
        self.clear()
        self.refresh()

        self.wake()

        if not self.visible:
            self.show()

    def display_image_file(self, file_path_or_url, xy=None, invert=False):
        """Render a static image to the screen from a file or URL at a given
        position.

        The display's positional properties (e.g. `top_left`, `top_right`) can be used to assist with
        specifying the `xy` position parameter.

        :param str file_path_or_url: A file path or URL to the image
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param bool invert: Set to True to flip the on/off state of each pixel in the image
        """
        self.display_image(
            ImageFunctions.get_pil_image_from_path(file_path_or_url),
            xy=xy,
            invert=invert,
        )

    # TODO: add 'size' parameter
    # TODO: add 'fill', 'stretch', 'crop', etc. to OLED images - currently, they only stretch by default
    # TODO: handle 'xy'
    def display_image(self, image, xy=None, invert=False):
        """Render a static image to the screen from a file or URL at a given
        position.

        The image should be provided as a PIL Image object.

        :param Image image: A PIL Image object to be rendered
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param bool invert: Set to True to flip the on/off state of each pixel in the image
        """
        self.__display(
            self.assistant.process_image(ImageFunctions.convert(image, format="PIL")),
            invert=invert,
        )

    def display_text(
        self,
        text,
        xy=None,
        font_size=None,
        font=None,
        invert=False,
        align=None,
        anchor=None,
    ):
        """Renders a single line of text to the screen at a given position and
        size.

        The display's positional properties (e.g. `top_left`, `top_right`) can be used to assist with
        specifying the `xy` position parameter.

        :param string text: The text to render
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param int font_size: The font size in pixels. If not provided or passed as
            `None`, the default font size will be used
        :param string font: A filename or path of a TrueType or OpenType font.
            If not provided or passed as `None`, the default font will be used
        :param bool invert: Set to True to flip the on/off state of each pixel in the image
        :param str align: PIL ImageDraw alignment to use
        :param str anchor: PIL ImageDraw text anchor to use
        """
        image = self.assistant.empty_image
        self.assistant.render_text(
            image,
            text,
            xy=xy,
            font_size=font_size,
            font=font,
            align=align,
            anchor=anchor,
            wrap=False,
        )
        self.display_image(image, invert=invert)

    def display_multiline_text(
        self,
        text,
        xy=None,
        font_size=None,
        font=None,
        invert=False,
        anchor=None,
        align=None,
    ):
        """Renders multi-lined text to the screen at a given position and size.
        Text that is too long for the screen will automatically wrap to the
        next line.

        The display's positional properties (e.g. `top_left`, `top_right`) can be used to assist with
        specifying the `xy` position parameter.

        :param string text: The text to render
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param int font_size: The font size in pixels. If not provided or passed as
            `None`, the default font size will be used
        :param string font: A filename or path of a TrueType or OpenType font.
            If not provided or passed as `None`, the default font will be used
        :param bool invert: Set to True to flip the on/off state of each pixel in the image
        :param str align: PIL ImageDraw alignment to use
        :param str anchor: PIL ImageDraw text anchor to use
        """
        image = self.assistant.empty_image
        self.assistant.render_text(
            image,
            text,
            xy=xy,
            font_size=font_size,
            font=font,
            align=align,
            anchor=anchor,
        )
        self.display_image(image, invert=invert)

    def __display(self, image_to_display, force=False, invert=False):
        self.stop_animated_image()

        if invert:
            image_to_display = self.assistant.invert(image_to_display)

        self.__fps_regulator.stop_timer()

        if force or self.should_redisplay(image_to_display):
            self.device.display(image_to_display)

        self.__fps_regulator.start_timer()
        self.image = image_to_display.copy()

    def play_animated_image_file(self, file_path_or_url, background=False, loop=False):
        """Render an animated image to the screen from a file or URL.

        :param str file_path_or_url: A file path or URL to the image
        :param bool background: Set whether the image should be in a
            background thread or in the main thread.
        :param bool loop: Set whether the image animation should start
            again when it has finished
        """
        image = ImageFunctions.get_pil_image_from_path(file_path_or_url)
        self.play_animated_image(image, background, loop)

    def play_animated_image(self, image, background=False, loop=False):
        """Render an animation or a image to the screen.

        Use stop_animated_image() to end a background animation

        :param Image image: A PIL Image object to be rendered
        :param bool background: Set whether the image should be in a
            background thread or in the main thread.
        :param bool loop: Set whether the image animation should start
            again when it has finished
        """
        self.stop_animated_image()
        self.__kill_thread = False
        if background is True:
            self.__auto_play_thread = Thread(
                target=self.__auto_play, args=(image, loop), daemon=True
            )
            self.__auto_play_thread.start()
        else:
            self.__auto_play(image, loop)

    def stop_animated_image(self):
        """Stop background animation started using `start()`, if currently
        running."""
        if current_thread() is not main_thread():
            # thread that runs an animation in the background can't "join" itself
            return

        if self.__auto_play_thread is not None and self.__auto_play_thread.is_alive():
            self.__kill_thread = True
            self.__auto_play_thread.join()

    ##################################################
    # Position/dimension methods
    ##################################################
    @property
    def bounding_box(self):
        """Gets the bounding box of the miniscreen display.

        :return: The device's bounding box as an (top-left x, top-left
            y, bottom-right x, bottom-right y) tuple.
        :rtype: tuple
        """
        return self.device.bounding_box

    @property
    def center(self):
        """Gets the center of the miniscreen display.

        :return: The coordinates of the center of the display's bounding
            box as an (x,y) tuple.
        :rtype: tuple
        """
        return (self.width / 2, self.height / 2)

    @property
    def top_left(self):
        """Gets the top left corner of the miniscreen display.

        :return: The coordinates of the center of the display's bounding
            box as an (x,y) tuple.
        :rtype: tuple
        """
        return (self.bounding_box[0], self.bounding_box[1])

    @property
    def top_right(self):
        """Gets the top-right corner of the miniscreen display.

        :return: The coordinates of the top right of the display's
            bounding box as an (x,y) tuple.
        :rtype: tuple
        """
        return (self.bounding_box[2], self.bounding_box[1])

    @property
    def bottom_left(self):
        """Gets the bottom-left corner of the miniscreen display.

        :return: The coordinates of the bottom left of the display's
            bounding box as an (x,y) tuple.
        :rtype: tuple
        """
        return (self.bounding_box[0], self.bounding_box[3])

    @property
    def bottom_right(self):
        """Gets the bottom-right corner of the miniscreen display.

        :return: The coordinates of the bottom right of the display's
            bounding box as an (x,y) tuple.
        :rtype: tuple
        """
        return (self.bounding_box[2], self.bounding_box[3])

    #######################
    # Deprecation support #
    #######################
    def display(self, force=False):
        """Displays what is on the current canvas to the screen as a single
        frame.

        .. warning::
           This method is deprecated and will be deleted on the next major release of the SDK.

        This method does not need to be called when using the other `draw`
        functions in this class, but is used when the caller wants to use
        the *canvas* object to draw composite objects and then render them
        to screen in a single frame.
        """
        print(
            "'display()' is now deprecated. You will need to handle your own images in future."
        )
        self.__display(self._image, force=force)

    def draw(self):
        """..

        warning::
        This method is deprecated in favor of :func:`display_image` and
        :func:`display_text`, and will be deleted on the next major release of the SDK.
        """
        print("'draw()' is now deprecated. Using 'display()'...")
        self.display()

    def draw_image_file(self, file_path_or_url, xy=None):
        """..

        warning::
        This method is deprecated in favor of :func:`display_image_file`, and will be deleted on the next major release of the SDK.
        """
        print("draw_image_file is now deprecated. Using display_image_file...")
        self.display_image_file(file_path_or_url, xy)

    def draw_image(self, image, xy=None):
        """..

        warning::
        This method is deprecated in favor of :func:`display_image`, and will be deleted on the next major release of the SDK.
        """
        print("draw_image is now deprecated. Using display_image...")
        self.display_image(image, xy)

    def draw_text(self, text, xy=None, font_size=None):
        """..

        warning::
        This method is deprecated in favor of :func:`display_text`, and will be deleted on the next major release of the SDK.
        """
        print("draw_text is now deprecated. Using display_text...")
        self.display_text(text, xy, font_size)

    def draw_multiline_text(self, text, xy=None, font_size=None):
        """..

        warning::
        This method is deprecated in favor of :func:`display_multiline_text`, and will be deleted on the next major release of the SDK.
        """
        print("draw_multiline_text is now deprecated. Using display_multiline_text...")
        self.display_multiline_text(text, xy, font_size)

    ####################
    # Internal support #
    ####################
    def __auto_play(self, image, loop=False):
        while True:
            for frame in self.assistant.get_frame_iterator(image):
                if self.__kill_thread:
                    break

                self.display_image(frame)
                # Wait for animated image's frame length
                sleep(float(frame.info["duration"] / 1000))  # ms to s

            if self.__kill_thread or not loop:
                self.reset()
                break

    def __cleanup(self):
        self.stop_animated_image()
        self._ptdm_subscribe_client.stop_listening()
