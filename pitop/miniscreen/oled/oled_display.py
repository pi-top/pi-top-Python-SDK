from .controls import (  # noqa: F401
    device_is_active,
    reset_device,
    get_device,
    set_control_to_pi,
    set_control_to_hub,
)
from .oled_image import OLEDImage
from .core.canvas import Canvas
from .core.fps_regulator import FPS_Regulator

from pitopcommon.sys_info import is_pi


from copy import deepcopy
from PIL import Image
from threading import Thread


class OLED:
    """
    Provides access to the OLED screen on the pi-top [4], and exposes methods
    for simple rendering of text or images to the screen.
    """

    def __init__(self):
        self._visible = False
        self.image = Image.new(get_device().mode,
                               get_device().size)
        self.canvas = Canvas(get_device(), self.image)
        self.fps_regulator = FPS_Regulator()
        self._previous_frame = None
        self.auto_play_thread = None

        self.reset()

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
        get_device().hide()
        self._visible = False

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as draw()
        has not been called)
        """
        get_device().show()
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
        if is_pi():
            set_control_to_pi()
        self.canvas.clear()
        get_device().display(self.image)
        get_device().contrast(255)
        self.show()

    def draw_image_file(self, file_path, xy=None):
        """
        Renders a static image file to the screen at a given position.

        The helper methods in the `pitop.miniscreen.oled.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param OLEDImage image: An `OLEDImage` object to be rendered
        :param tuple xy: The position on the screen to render the image. If not
            provided or passed as `None` the image will be drawn in the top-left of
            the screen.
        """
        image = OLEDImage(file_path)
        self.draw_image(image, xy)

    def draw_image(self, image, xy=None):
        """
        Renders an image to the screen at a given position.

        The image should be provided as a `pitop.miniscreen.oled.OLEDImage` object, which can be
        used to animate an image with frames (e.g. an animated gif).

        The helper methods in the `pitop.miniscreen.oled.Canvas` class can be used to specify the
        `xy` position parameter, e.g. `top_left`, `top_right`.

        :param OLEDImage image: An `OLEDImage` object to be rendered
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

        The helper methods in the pitop.miniscreen.oled.Canvas class can be used to specify the
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

        The helper methods in the `pitop.miniscreen.oled.Canvas` class can be used to specify the
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
            get_device().display(self.image)

        self.fps_regulator.start_timer()
        self._previous_frame = Canvas(get_device(), deepcopy(self.image))

    def play_animated_image(self, image, background=False):
        """
        Render an animation or a image to the screen.

        :param OLEDImage image: An `OLEDImage` object to be rendered
        :param bool background: Set whether the image should be in a background thread
            or in the main thread.
        """
        self._kill_thread = False
        if background is True:
            self.auto_play_thread = Thread(
                target=self._auto_play, args=(image,))
            self.auto_play_thread.start()
        else:
            self._auto_play(image)

    def stop_animated_image(self):
        """
        Stop background animation started using `start()`, if currently running.
        """
        if self.auto_play_thread is not None:
            self._kill_thread = True
            self.auto_play_thread.join()

    def _auto_play(self, image):
        while not image.finished or image.loop is True:
            if self._kill_thread:
                break
            self.draw_image(image)
            image.next_frame()
