from time import perf_counter

from PIL import Image, ImageDraw

from . import mixin


class hotspot(mixin.capabilities):
    """A hotspot (`a place of more than usual interest, activity, or
    popularity`)

    is a live display which may be added to a virtual viewport - if the hotspot
    and the viewport are overlapping, then the :func:`update` method will be
    automatically invoked when the viewport is being refreshed or its position
    moved (such that an overlap occurs).

    You would either:

        * create a ``hotspot`` instance, suppling a render function (taking an
          :py:mod:`PIL.ImageDraw` object, ``width`` & ``height`` dimensions.
          The render function should draw within a bounding box of ``(0, 0,
          width, height)``, and render a full frame.

        * sub-class ``hotspot`` and override the :func:`should_redraw` and
          :func:`update` methods. This might be more useful for slow-changing
          values where it is not necessary to update every refresh cycle, or
          your implementation is stateful.
    """

    def __init__(self, width, height, draw_fn=None):
        self.capabilities(width, height, rotate=0)  # TODO: set mode?
        self._fn = draw_fn

    def paste_into(self, image, xy):
        im = Image.new(image.mode, self.size)
        draw = ImageDraw.Draw(im)
        self.update(draw)
        image.paste(im, xy)
        del draw
        del im

    def should_redraw(self):
        """Override this method to return true or false on some condition
        (possibly on last updated member variable) so that for slow changing
        hotspots they are not updated too frequently."""
        return True

    def update(self, draw):
        if self._fn:
            self._fn(draw, self.width, self.height)


class snapshot(hotspot):
    """A snapshot is a `type of` hotspot, but only updates once in a given
    interval, usually much less frequently than the viewport requests refresh
    updates."""

    def __init__(self, width, height, draw_fn=None, interval=1.0):
        assert interval > 0
        super(snapshot, self).__init__(width, height, draw_fn)
        self.interval = interval
        self.last_updated = -interval

    def should_redraw(self):
        """Only requests a redraw after ``interval`` seconds have elapsed."""
        return perf_counter() - self.last_updated > self.interval

    def paste_into(self, image, xy):
        super(snapshot, self).paste_into(image, xy)
        self.last_updated = perf_counter()
