from .core.controls import (
    device_is_active as _device_is_active,
    reset_device as _reset_device,
    get_device as _get_device,
    set_control_to_pi as _set_control_to_pi,
    set_control_to_hub as _set_control_to_hub,
    _set_exclusive_mode
)
from .core.canvas import Canvas
from .core.fps_regulator import FPS_Regulator
from .core.image_helper import (
    get_pil_image_from_path,
    process_pil_image_frame,
)

from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message,
)

import atexit
from copy import deepcopy
from PIL import Image, ImageSequence
from threading import Thread
from time import sleep


class OLED:
    """
    Provides access to the OLED screen on the pi-top [4], and exposes methods
    for simple rendering of text or images to the screen.
    """

    def __init__(self):
        self._visible = False
        self.device = _get_device()
        self.image = Image.new(self.device.mode,
                               self.device.size)
        self.canvas = Canvas(self.device, self.image)
        self.fps_regulator = FPS_Regulator()
        self._previous_frame = None
        self.auto_play_thread = None

        self.reset()

        self.when_pi_takes_control = None
        self.when_hub_takes_control = None

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def on_control_changed(parameters):
            controller = int(parameters[0])

            if controller == 1:
                self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_pi_takes_control)
            else:
                self.__ptdm_subscribe_client.invoke_callback_func_if_exists(self.when_hub_takes_control)

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise({
            Message.PUB_OLED_CONTROL_CHANGED: on_control_changed,
        })
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    def is_active(self):
        return _device_is_active()

    def set_control_to_pi(self):
        _set_control_to_pi()

    def set_control_to_hub(self):
        _set_control_to_hub()

    # Only intended to be used by pt-sys-oled
    def _set_exclusive_mode(self, val: bool):
        _set_exclusive_mode(val)

    def set_max_fps(self, max_fps):
        """
        Set the maximum frames per second that the OLED screen can
        display. This method can be useful to control or limit the speed
        of animations.

        :param int max_fps: The maximum frames that can be rendered per second
        """
        self.fps_regulator.set_max_fps(max_fps)

    def hide(self):
        """
        The pi-top OLED display is put into low power mode. The previously
        shown image will re-appear when show() is given, even if the
        internal frame buffer has been changed (so long as draw() has not
        been called).
        """
        self.device.hide()
        self._visible = False

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as draw()
        has not been called)
        """
        self.device.show()
        self._visible = True

    def is_hidden(self):
        """
        Returns whether the device is currently in low power state
        :return: whether the the screen is in low power mode
        :rtype: bool
        """
        return self._visible

    def reset(self):
        """
        Gives the caller access to the OLED screen (i.e. in the case the the system is
        currently rendering information to the screen) and clears the screen.
        """
        self.set_control_to_pi()
        self.canvas.clear()

        _reset_device()
        self.device = _get_device()

        self.device.display(self.image)
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
            xy = self.canvas.top_left()

        self.canvas.clear()
        self.canvas.image(xy, image)

        self.draw()

    def _draw_text_base(self, text_func, text, font_size, xy):
        self.canvas.clear()

        if font_size is not None:
            previous_font_size = self.canvas.font_size
            self.canvas.set_font_size(font_size)

        text_func(xy, text, fill=1, spacing=0, align="left")
        self.draw()

        if font_size is not None:
            self.canvas.set_font_size(previous_font_size)

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
            xy = self.canvas.top_left()

        self._draw_text_base(self.canvas.text, text, font_size, xy)

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
            xy = self.canvas.top_left()

        self._draw_text_base(self.canvas.multiline_text, text, font_size, xy)

    def draw(self):
        """
        Draws what is on the current canvas to the screen as a single frame.

        This method does not need to be called when using the other `draw`
        functions in this class, but is used when the caller wants to use
        the *canvas* object to draw composite objects and then render them
        to screen in a single frame.
        """
        self.fps_regulator.stop_timer()
        paint_to_screen = False
        if self._previous_frame is None:
            paint_to_screen = True
        else:
            prev_pix = self._previous_frame.get_pixels()
            current_pix = self.canvas.get_pixels()
            if (prev_pix != current_pix).any():
                paint_to_screen = True

        if paint_to_screen:
            self.device.display(self.image)

        self.fps_regulator.start_timer()
        self._previous_frame = Canvas(self.device, deepcopy(self.image))

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
            self.auto_play_thread = Thread(
                target=self.__auto_play, args=(image, loop))
            self.auto_play_thread.start()
        else:
            self.__auto_play(image)

    def stop_animated_image(self):
        """
        Stop background animation started using `start()`, if currently running.
        """
        if self.auto_play_thread is not None:
            self.__kill_thread = True
            self.auto_play_thread.join()

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
