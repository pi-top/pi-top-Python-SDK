from .core.canvas import Canvas
from .core.device_controller import OledDeviceController
from .core.fps_regulator import FPS_Regulator
from .core.image_helper import (
    get_pil_image_from_path,
    process_pil_image_frame,
)

from atexit import register
from copy import deepcopy
from PIL import Image, ImageSequence
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

    LOCK_FILE_PATH = "/tmp/pt-oled.lock"

    def __init__(self, exclusive_mode=True):
        self.controller = OledDeviceController(self.reset, exclusive_mode)

        self.__image = None
        self.__canvas = None

        self.image = Image.new(
            self.device.mode,
            self.device.size
        )

        self.__fps_regulator = FPS_Regulator()

        self.__visible = False
        self.__previous_frame = None
        self.__auto_play_thread = None

        self.__file_monitor_thread = None
        self.__when_user_stops_using_oled = None
        self.__when_user_starts_using_oled = None

        self.reset()

        register(self.__cleanup)

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, image):
        self.__image = image
        self.__canvas = Canvas(self.device, self.__image)

    @property
    def spi_bus(self):
        return self.controller.spi_bus

    @spi_bus.setter
    def spi_bus(self, bus):
        self.controller.spi_bus = bus

    @property
    def device(self):
        return self.controller.get_device()

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

    def is_active(self):
        return self.controller.device_is_active()

    def set_control_to_pi(self):
        self.controller.set_control_to_pi()

    def set_control_to_hub(self):
        self.controller.set_control_to_hub()

    # Only intended to be used by pt-sys-oled
    def _set_exclusive_mode(self, val: bool):
        self.controller.set_exclusive_mode(val)

    def set_max_fps(self, max_fps):
        """
        Set the maximum frames per second that the OLED screen can
        display. This method can be useful to control or limit the speed
        of animations.

        :param int max_fps: The maximum frames that can be rendered per second
        """
        self.__fps_regulator.set_max_fps(max_fps)

    def hide(self):
        """
        The pi-top OLED display is put into low power mode. The previously
        shown image will re-appear when show() is given, even if the
        internal frame buffer has been changed (so long as draw() has not
        been called).
        """
        self.device.hide()
        self.__visible = False

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as draw()
        has not been called)
        """
        self.device.show()
        self.__visible = True

    @property
    def is_hidden(self):
        """
        Returns whether the device is currently in low power state
        :return: whether the the screen is in low power mode
        :rtype: bool
        """
        return not self.__visible

    def contrast(self, new_contrast_value):
        assert new_contrast_value in range(0, 256)

        self.device.contrast(new_contrast_value)

    def wake(self):
        self.contrast(255)

    def sleep(self):
        self.contrast(0)

    def reset(self, reset_controller=True):
        """
        Gives the caller access to the OLED screen (i.e. in the case the the system is
        currently rendering information to the screen) and clears the screen.
        """
        self.set_control_to_pi()
        self.__canvas.clear()

        if reset_controller:
            self.controller.reset_device()

        self.device.display(self.__image)
        self.device.contrast(255)

        self.show()

    def __process_image_frame(self, image):
        return process_pil_image_frame(
            image,
            self.device.size,
            self.device.mode
        )

    def draw_image_file(self, file_path_or_url, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The helper methods in the `pitop.miniscreen.oled.core.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param str file_path_or_url: A file path or URL to the image
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        image = get_pil_image_from_path(file_path_or_url)
        self.draw_image(self.__process_image_frame(image), xy)

    def draw_image(self, image, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The image should be provided as a PIL Image object.

        The helper methods in the `pitop.miniscreen.oled.core.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param Image image: A PIL Image object to be rendered
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        if xy is None:
            xy = self.__canvas.top_left()

        self.__canvas.clear()
        self.__canvas.image(xy, image)

        self.draw()

    def _draw_text_base(self, text_func, text, font_size, xy):
        self.__canvas.clear()

        if font_size is not None:
            previous_font_size = self.__canvas.font_size
            self.__canvas.set_font_size(font_size)

        text_func(xy, text, fill=1, spacing=0, align="left")
        self.draw()

        if font_size is not None:
            self.__canvas.set_font_size(previous_font_size)

    def draw_text(self, text, xy=None, font_size=None):
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
            xy = self.__canvas.top_left()

        self._draw_text_base(self.__canvas.text, text, font_size, xy)

    def draw_multiline_text(self, text, xy=None, font_size=None):
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
            xy = self.__canvas.top_left()

        self._draw_text_base(self.__canvas.multiline_text, text, font_size, xy)

    def draw(self):
        """
        Draws what is on the current canvas to the screen as a single frame.

        This method does not need to be called when using the other `draw`
        functions in this class, but is used when the caller wants to use
        the *canvas* object to draw composite objects and then render them
        to screen in a single frame.
        """
        self.__fps_regulator.stop_timer()
        paint_to_screen = False
        if self.__previous_frame is None:
            paint_to_screen = True
        else:
            prev_pix = self.__previous_frame.get_pixels()
            current_pix = self.__canvas.get_pixels()
            if (prev_pix != current_pix).any():
                paint_to_screen = True

        if paint_to_screen:
            self.device.display(self.__image)

        self.__fps_regulator.start_timer()
        self.__previous_frame = Canvas(self.device, deepcopy(self.__image))

    def play_animated_image_file(self, file_path_or_url, background=False, loop=False):
        """
        Render an animated image to the screen from a file or URL.

        :param str file_path_or_url: A file path or URL to the image
        :param bool background: Set whether the image should be in a background thread
            or in the main thread.
        :param bool loop: Set whether the image animation should start again when it
            has finished
        """
        image = get_pil_image_from_path(file_path_or_url)
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
            self.__auto_play(image)

    def stop_animated_image(self):
        """
        Stop background animation started using `start()`, if currently running.
        """
        if self.__auto_play_thread is not None:
            self.__kill_thread = True
            self.__auto_play_thread.join()

    def __auto_play(self, image, loop=False):
        while True:
            for frame in ImageSequence.Iterator(image):

                if self.__kill_thread:
                    break

                self.draw_image(
                    self.__process_image_frame(frame)
                )
                # Wait for animated image's frame length
                sleep(
                    float(frame.info["duration"] / 1000)  # ms to s
                )

            if self.__kill_thread or not loop:
                self.reset()
                break

    @property
    def when_user_starts_using_oled(self):
        return self.__when_user_starts_using_oled

    @when_user_starts_using_oled.setter
    def when_user_starts_using_oled(self, callback):
        if not callable(callback):
            raise ValueError("Callback must be callable")

        if self.__when_user_starts_using_oled is not None:
            self.__file_monitor_thread.join(0)

        self.__when_user_starts_using_oled = callback
        self.__start_lockfile_monitoring_thread()

    @property
    def when_user_stops_using_oled(self):
        return self.__when_user_stops_using_oled

    @when_user_stops_using_oled.setter
    def when_user_stops_using_oled(self, callback):
        if not callable(callback):
            raise ValueError("Callback must be callable")

        if self.__when_user_stops_using_oled is not None:
            self.__file_monitor_thread.join(0)

        self.__when_user_stops_using_oled = callback
        self.__start_lockfile_monitoring_thread()

    def __start_lockfile_monitoring(self):
        eh = ProcessEvent()
        events_to_watch = 0
        if self.__when_user_stops_using_oled:
            eh.process_IN_CLOSE_WRITE = lambda event: self.__when_user_stops_using_oled()
            events_to_watch = events_to_watch | IN_CLOSE_WRITE
        if self.__when_user_starts_using_oled:
            eh.process_IN_OPEN = lambda event: self.__when_user_starts_using_oled()
            events_to_watch = events_to_watch | IN_OPEN

        wm = WatchManager()
        wm.add_watch(self.LOCK_FILE_PATH, events_to_watch)
        notifier = Notifier(wm, eh)
        notifier.loop()

    def __start_lockfile_monitoring_thread(self):
        self.__cleanup()
        self.__file_monitor_thread = Thread(target=self.__start_lockfile_monitoring)
        self.__file_monitor_thread.daemon = True
        self.__file_monitor_thread.start()

    def __cleanup(self):
        if self.__file_monitor_thread is not None and self.__file_monitor_thread.is_alive():
            self.__file_monitor_thread.join(0)
