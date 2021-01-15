from .core.canvas import Canvas
from .core.device_controller import OledDeviceController

from pitopcommon.formatting import is_url

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
try:
    from time import monotonic
except ImportError:
    from monotonic import monotonic
from urllib.request import urlopen


class FPS_Regulator(object):
    """
    Adapted from ``luma.core.spritesheet``

    Implements a variable sleep mechanism to give the appearance of a consistent
    frame rate. Using a fixed-time sleep will cause animations to be jittery
    (looking like they are speeding up or slowing down, depending on what other
    work is occurring), whereas this class keeps track of when the last time the
    ``sleep()`` method was called, and calculates a sleep period to smooth out
    the jitter.
    :param fps: The max frame rate, expressed numerically in
        frames-per-second.  By default, this is set at 16.67, to give a frame
        render time of approximately 60ms. This can be overridden as necessary,
        and if no FPS limiting is required, the ``fps`` can be set to zero.
    :type fps: float
    """

    def __init__(self, max_fps=16.67):
        self.set_max_fps(max_fps)
        self.total_transit_time = 0
        self.start_time = None
        self.last_time = None
        self.fps = 30

    def set_max_fps(self, max_fps):
        """
        Sets the max frame rate to the value provided

        Parameters
        ----------
        max_fps : int
          The frame rate that the user aims to render to the screen at. Lower frame rates are permitted.
        """
        self.total_no_of_frames = 0
        if max_fps == 0:
            max_fps = -1
        self.max_sleep_time = 1.0 / max_fps

    def throttle_fps_if_needed(self):
        """
        Sleep to ensure that max frame rate is not exceeded
        """
        if self.max_sleep_time >= 0:
            last_frame_transit_time = monotonic() - self.last_time
            sleep_for = self.max_sleep_time - last_frame_transit_time

            if sleep_for > 0:
                sleep(sleep_for)

    def start_timer(self):
        """
        Starts internal timer so that time taken to render frame can be known
        """
        self.enter_time = monotonic()
        if not self.start_time:
            self.start_time = self.enter_time
            self.last_time = self.enter_time

    def stop_timer(self):
        """
        Stops internal timer so that time taken to render frame can be known. Responsible for throttling frame rate as
         required
        """
        try:
            self.total_transit_time += monotonic() - self.enter_time
            self.total_no_of_frames += 1
            self.throttle_fps_if_needed()

            self.last_time = monotonic()
        except AttributeError:
            pass

    def effective_FPS(self):
        """
        Calculates the effective frames-per-second - this should largely
        correlate to the max FPS supplied in the constructor, but no
        guarantees are given.
        :returns: the effective frame rate
        :rtype: float
        """
        if self.start_time is None:
            self.start_time = 0
        elapsed = monotonic() - self.start_time
        return self.total_no_of_frames / elapsed

    def average_transit_time(self):
        """
        Calculates the average transit time between the enter and exit methods,
        and return the time in milliseconds
        :returns: the average transit in milliseconds
        :rtype: float
        """
        return self.total_transit_time * 1000.0 / self.total_no_of_frames


class OLED:
    """
    Provides access to the OLED screen on the pi-top [4], and exposes methods
    for simple rendering of text or images to the screen.
    """

    LOCK_FILE_PATH = "/tmp/pt-oled.lock"

    # Exclusive mode only intended to be used privately (pt-sys-oled, some CLI operations)
    def __init__(self, _exclusive_mode=True):
        self.controller = OledDeviceController(self.reset, _exclusive_mode)

        self.__image = Image.new(
            self.device.mode,
            self.device.size
        )
        self.__canvas = Canvas(self.device, self.__image)
        self.__rendered_canvas = None
        self.update_rendered_canvas()

        self.__fps_regulator = FPS_Regulator()

        self.__visible = False
        self.__auto_play_thread = None

        # Lock file monitoring - used by pt-sys-oled
        self.__file_monitor_thread = None
        self.__when_user_stops_using_oled = None
        self.__when_user_starts_using_oled = None

        self.reset()

        register(self.__cleanup)

    def update_rendered_canvas(self):
        self.__rendered_canvas = Canvas(self.device, deepcopy(self.__image))

    @property
    def image(self):
        # Return the last image that was sent to the display
        return self.__rendered_canvas.image

    @property
    def canvas_image(self):
        # Return the image that is being prepared for the display
        return self.__image

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

        self.__send_image_to_device()
        self.device.contrast(255)

        self.show()

    def draw_image_file(self, file_path_or_url, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The helper methods in the `pitop.miniscreen.core.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param str file_path_or_url: A file path or URL to the image
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        self.draw_image(self.__get_pil_image_from_path(file_path_or_url), xy)

    # TODO: add 'size' parameter for images being rendered to canvas
    def draw_image(self, image, xy=None):
        """
        Render a static image to the screen from a file or URL at a given position.

        The image should be provided as a PIL Image object.

        The helper methods in the `pitop.miniscreen.core.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param Image image: A PIL Image object to be rendered
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        if xy is None:
            xy = self.__canvas.top_left()

        self.__canvas.clear()
        self.__canvas.draw_image(xy, image)

        self.draw()

    def __draw_text_base(self, text_func, text, font_size, xy):
        self.canvas.clear()

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

        The helper methods in the pitop.miniscreen.core.Canvas class can be used to specify the
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

        self.__draw_text_base(self.__canvas.draw_text, text, font_size, xy)

    def draw_multiline_text(self, text, xy=None, font_size=None):
        """
        Renders multi-lined text to the screen at a given position and size. Text that
        is too long for the screen will automatically wrap to the next line.

        The helper methods in the `pitop.miniscreen.core.Canvas` class can be used to specify the
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

        self.__draw_text_base(self.__canvas.draw_multiline_text, text, font_size, xy)

    def __send_image_to_device(self):
        self.device.display(self.__image)

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
        if self.__rendered_canvas is None:
            paint_to_screen = True
        else:
            # TODO: find a faster way of checking if pixel data has changed
            prev_pix = self.__rendered_canvas.get_pixels()
            current_pix = self.__canvas.get_pixels()
            if (prev_pix != current_pix).any():
                paint_to_screen = True

        if paint_to_screen:
            self.__send_image_to_device()

        self.__fps_regulator.start_timer()
        self.update_rendered_canvas()

    def play_animated_image_file(self, file_path_or_url, background=False, loop=False):
        """
        Render an animated image to the screen from a file or URL.

        :param str file_path_or_url: A file path or URL to the image
        :param bool background: Set whether the image should be in a background thread
            or in the main thread.
        :param bool loop: Set whether the image animation should start again when it
            has finished
        """
        image = self.__get_pil_image_from_path(file_path_or_url)
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

                self.draw_image(frame)
                # Wait for animated image's frame length
                sleep(
                    float(frame.info["duration"] / 1000)  # ms to s
                )

            if self.__kill_thread or not loop:
                self.reset()
                break

    def __get_pil_image_from_path(self, file_path_or_url):
        if is_url(file_path_or_url):
            image_path = urlopen(file_path_or_url)
        else:
            image_path = file_path_or_url

        image = Image.open(image_path)

        # Verify on deep copy to avoid needing to close and
        # re-open after verifying...
        test_image = image.copy()
        # Raise exception if there's an issue with the image
        test_image.verify()

        return image

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
            wm.add_watch(self.LOCK_FILE_PATH, events_to_watch)
            notifier = Notifier(wm, eh)
            notifier.loop()

        self.__cleanup()
        self.__file_monitor_thread = Thread(target=start_lockfile_monitoring)
        self.__file_monitor_thread.daemon = True
        self.__file_monitor_thread.start()

    def __cleanup(self):
        if self.__file_monitor_thread is not None and self.__file_monitor_thread.is_alive():
            self.__file_monitor_thread.join(0)
