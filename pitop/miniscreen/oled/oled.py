from pitop.core import ImageFunctions
from .core import (
    Canvas,
    FPS_Regulator,
    OledDeviceController,
)


from atexit import register
from os.path import isfile
from PIL import (
    Image,
    ImageChops,
    ImageDraw,
    ImageFont,
    ImageSequence,
)
from pyinotify import (
    IN_CLOSE_WRITE,
    IN_OPEN,
    Notifier,
    ProcessEvent,
    WatchManager,
)
from threading import Thread
from time import sleep


class OLED:
    """
    Provides access to the OLED screen on the pi-top [4], and exposes methods
    for simple rendering of text or images to the screen.
    """

    __LOCK_FILE_PATH = "/tmp/pt-oled.lock"

    # Exclusive mode only intended to be used privately (pt-sys-oled, some CLI operations)
    def __init__(self, _exclusive_mode=True):
        self.__controller = OledDeviceController(self._redraw_last_image, _exclusive_mode)

        self.image = Image.new(
            self.device.mode,
            self.device.size
        )

        self._image = self.image.copy()

        self.canvas = Canvas(self._image)

        self.__fps_regulator = FPS_Regulator()

        self.__visible = False
        self.__auto_play_thread = None

        # Lock file monitoring - used by pt-sys-oled
        self.__file_monitor_thread = None
        self.__when_user_stops_using_oled = None
        self.__when_user_starts_using_oled = None

        self.reset()

        register(self.__cleanup)

    def prepare_image(self, image_to_prepare):
        return self.canvas.process_image(image_to_prepare)

    def should_redisplay(self):
        return self.image is None or \
            ImageChops.difference(self.image, self._image).getbbox()

    @property
    def spi_bus(self):
        return self.__controller.spi_bus

    @spi_bus.setter
    def spi_bus(self, bus):
        self.__controller.spi_bus = bus

    @property
    def device(self):
        return self.__controller.get_device()

    @property
    def size(self):
        return self.device.size

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def mode(self):
        return self.device.mode

    @property
    def is_active(self):
        return self.__controller.device_is_active()

    @property
    def visible(self):
        """
        Returns whether the device is currently in low power state
        :return: whether the the screen is in low power mode
        :rtype: bool
        """
        return not self.__visible

    def set_control_to_pi(self):
        self.__controller.set_control_to_pi()

    def set_control_to_hub(self):
        self.__controller.set_control_to_hub()

    def set_max_fps(self, max_fps):
        """
        Set the maximum frames per second that the OLED screen can
        display. This method can be useful to control or limit the speed
        of animations.

        This works by blocking on the OLED's display methods if called before
        the amount of time that a frame should last is not exceeded.

        :param int max_fps: The maximum frames that can be rendered per second
        """
        self.__fps_regulator.set_max_fps(max_fps)

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as display()
        has not been called)
        """
        self.device.show()
        self.__visible = True

    def hide(self):
        """
        The pi-top OLED display is put into low power mode. The previously
        shown image will re-appear when show() is given, even if the
        internal frame buffer has been changed (so long as display() has not
        been called).
        """
        self.device.hide()
        self.__visible = False

    def contrast(self, new_contrast_value):
        assert new_contrast_value in range(0, 256)

        self.device.contrast(new_contrast_value)

    def wake(self):
        self.contrast(255)

    def sleep(self):
        self.contrast(0)

    def clear(self):
        self.canvas.rectangle(self.bounding_box, fill=0)
        self.__display(self._image, force=True)

    # TODO: evaluate dropping this 'redraw last image' function at v1.0.0
    #
    # this is only necessary to support users with SPI0 on device
    # with older SDK version that only supported SPI1
    def _redraw_last_image(self):
        self.__display(self.image, force=True)

    def refresh(self):
        self.set_control_to_pi()
        self.__controller.reset_device()
        self._redraw_last_image()

    def reset(self, force=True):
        """
        Gives the caller access to the OLED screen (i.e. in the case the the system is
        currently rendering information to the screen) and clears the screen.
        """
        self.clear()
        self.refresh()

        self.wake()

        if not self.visible:
            self.show()

    def display_image_file(self, file_path_or_url, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The helper methods in the `pitop.miniscreen.oled.core.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param str file_path_or_url: A file path or URL to the image
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        self.display_image(ImageFunctions.get_pil_image_from_path(file_path_or_url), xy)

    # TODO: add 'size' parameter for images being rendered to canvas
    # TODO: add 'fill', 'stretch', 'crop', etc. to OLED images - currently, they only stretch by default
    def display_image(self, image, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The image should be provided as a PIL Image object.

        :param Image image: A PIL Image object to be rendered
        """
        self.__display(self.prepare_image(image))

    def display_text(self, text, xy=None, font_size=None):
        """
        Renders a single line of text to the screen at a given position and size.

        The helper methods in the pitop.miniscreen.oled.core.Canvas class can be used to specify the
        position, e.g. `top_left`, `top_right`.

        :param string text: The text to render
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param int font_size: The font size in pixels. If not provided or passed as
            `None`, the default font size will be used
        """
        if xy is None:
            xy = self.top_left

        if font_size is None:
            font_size = 30

        # Create empty image
        image = Image.new(
            self.device.mode,
            self.device.size
        )

        primary_font_path = "/usr/share/fonts/opentype/FSMePro/FSMePro-Light.otf"
        fallback_font_path = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

        # 'Draw' text to empty image, using desired font size
        ImageDraw.Draw(image).text(
            xy,
            text,
            font=ImageFont.truetype(
                primary_font_path if isfile(primary_font_path) else fallback_font_path,
                size=font_size
            ),
            fill=1,
            spacing=0,
            align="left"
        )

        # Display image
        self.display_image(image)

    def display_multiline_text(self, text, xy=None, font_size=None):
        """
        Renders multi-lined text to the screen at a given position and size. Text that
        is too long for the screen will automatically wrap to the next line.

        The helper methods in the `pitop.miniscreen.oled.core.Canvas` class can be used to specify the
        position, e.g. `top_left`, `top_right`.

        :param string text: The text to render
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        :param int font_size: The font size in pixels. If not provided or passed as
            `None`, the default font size will be used
        """
        if xy is None:
            xy = self.top_left

        if font_size is None:
            font_size = 30

        # Create empty image
        image = Image.new(
            self.device.mode,
            self.device.size
        )

        primary_font_path = "/usr/share/fonts/opentype/FSMePro/FSMePro-Light.otf"
        fallback_font_path = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

        # 'Draw' text to empty image, using desired font size
        ImageDraw.Draw(image).multiline_text(
            xy,
            text,
            font=ImageFont.truetype(
                primary_font_path if isfile(primary_font_path) else fallback_font_path,
                size=font_size
            ),
            fill=1,
            spacing=0,
            align="left"
        )

        # Display image
        self.display_image(image)

    def __display(self, image_to_display, force=False):
        self.__fps_regulator.stop_timer()

        if force or self.should_redisplay():
            self.device.display(image_to_display)

        self.__fps_regulator.start_timer()
        self.image = image_to_display.copy()

    def play_animated_image_file(self, file_path_or_url, background=False, loop=False):
        """
        Render an animated image to the screen from a file or URL.

        :param str file_path_or_url: A file path or URL to the image
        :param bool background: Set whether the image should be in a background thread
            or in the main thread.
        :param bool loop: Set whether the image animation should start again when it
            has finished
        """
        image = ImageFunctions.get_pil_image_from_path(file_path_or_url)
        self.play_animated_image(image, background, loop)

    def play_animated_image(self, image, background=False, loop=False):
        """
        Render an animation or a image to the screen.

        Use stop_animated_image() to end a background animation

        :param Image image: A PIL Image object to be rendered
        :param bool background: Set whether the image should be in a background thread
            or in the main thread.
        :param bool loop: Set whether the image animation should start again when it
            has finished
        """
        self.__kill_thread = False
        if background is True:
            self.__auto_play_thread = Thread(
                target=self.__auto_play, args=(image, loop))
            self.__auto_play_thread.start()
        else:
            self.__auto_play(image, loop)

    def stop_animated_image(self):
        """
        Stop background animation started using `start()`, if currently running.
        """
        if self.__auto_play_thread is not None:
            self.__kill_thread = True
            self.__auto_play_thread.join()

    ##################################################
    # Position/dimension methods
    ##################################################
    @property
    def bounding_box(self):
        """
        Gets the bounding box of the pi-top OLED display.

        :return: The top-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return self.device.bounding_box

    @property
    def center(self):
        """
        Gets the center of the pi-top OLED display.

        :return: The top-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return (
            self.width / 2,
            self.height / 2
        )

    @property
    def top_left(self):
        """
        Gets the top left corner of the pi-top OLED display.

        :return: The top-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return (
            self.bounding_box[0],
            self.bounding_box[1]
        )

    @property
    def top_right(self):
        """
        Gets the top-right corner of the pi-top OLED display.

        :return: The top-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return (
            self.bounding_box[2],
            self.bounding_box[1]
        )

    @property
    def bottom_left(self):
        """
        Gets the bottom-left corner of the pi-top OLED display.

        :return: The bottom-left coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return (
            self.bounding_box[0],
            self.bounding_box[3]
        )

    @property
    def bottom_right(self):
        """
        Gets the bottom-right corner of the pi-top OLED display.

        :return: The bottom-right coordinates of the canvas bounding box as a tuple
        :rtype: tuple
        """
        return (
            self.bounding_box[2],
            self.bounding_box[3]
        )

    #######################
    # Deprecation support #
    #######################
    def display(self, force=False):
        """
        Displays what is on the current canvas to the screen as a single frame.

        This method does not need to be called when using the other `draw`
        functions in this class, but is used when the caller wants to use
        the *canvas* object to draw composite objects and then render them
        to screen in a single frame.
        """
        print("'display()' is now deprecated. You will need to handle your own images in future.")
        self.__display(self._image)

    def draw(self):
        print("'draw()' is now deprecated. Using 'display()'...")
        self.display()

    def draw_image_file(self, file_path_or_url, xy=None):
        print("draw_image_file is now deprecated. Using display_image_file...")
        self.display_image_file(file_path_or_url, xy)

    def draw_image(self, image, xy=None):
        print("draw_image is now deprecated. Using display_image...")
        self.display_image(image, xy)

    def draw_text(self, text, xy=None, font_size=None):
        print("draw_text is now deprecated. Using display_text...")
        self.display_text(text, xy, font_size)

    def draw_multiline_text(self, text, xy=None, font_size=None):
        print("draw_multiline_text is now deprecated. Using display_multiline_text...")
        self.display_multiline_text(text, xy, font_size)

    ####################
    # Internal support #
    ####################
    def __auto_play(self, image, loop=False):
        while True:
            for frame in ImageSequence.Iterator(image):

                if self.__kill_thread:
                    break

                self.display_image(frame)
                # Wait for animated image's frame length
                sleep(
                    float(frame.info["duration"] / 1000)  # ms to s
                )

            if self.__kill_thread or not loop:
                self.reset()
                break

    @property
    def _when_user_starts_using_oled(self):
        return self.__when_user_starts_using_oled

    @_when_user_starts_using_oled.setter
    def _when_user_starts_using_oled(self, callback):
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self.__when_user_starts_using_oled = callback
        # Lockfile thread needs to be restarted to get updated callback reference
        self.__start_lockfile_monitoring_thread()

    @property
    def _when_user_stops_using_oled(self):
        return self.__when_user_stops_using_oled

    @_when_user_stops_using_oled.setter
    def _when_user_stops_using_oled(self, callback):
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self.__when_user_stops_using_oled = callback
        # Lockfile thread needs to be restarted to get updated callback reference
        self.__start_lockfile_monitoring_thread()

    def __start_lockfile_monitoring_thread(self):

        def start_lockfile_monitoring():
            eh = ProcessEvent()
            events_to_watch = 0
            if self.__when_user_stops_using_oled:
                eh.process_IN_CLOSE_WRITE = lambda event: self.__when_user_stops_using_oled()
                events_to_watch = events_to_watch | IN_CLOSE_WRITE
            if self.__when_user_starts_using_oled:
                eh.process_IN_OPEN = lambda event: self.__when_user_starts_using_oled()
                events_to_watch = events_to_watch | IN_OPEN

            wm = WatchManager()
            wm.add_watch(self.__LOCK_FILE_PATH, events_to_watch)
            notifier = Notifier(wm, eh)
            notifier.loop()

        self.__cleanup()
        self.__file_monitor_thread = Thread(target=start_lockfile_monitoring)
        self.__file_monitor_thread.daemon = True
        self.__file_monitor_thread.start()

    def __cleanup(self):
        if self.__file_monitor_thread is not None and self.__file_monitor_thread.is_alive():
            self.__file_monitor_thread.join(0)
