# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.

from time import perf_counter

from PIL import Image, ImageDraw

from . import mixin
from .threadpool import threadpool

pool = threadpool(4)


def calc_bounds(xy, entity):
    """For an entity with width and height attributes, determine the bounding
    box if were positioned at ``(x, y)``."""
    left, top = xy
    right, bottom = left + entity.width, top + entity.height
    return [left, top, right, bottom]


def range_overlap(a_min, a_max, b_min, b_max):
    """Neither range is completely greater than the other."""
    return (a_min < b_max) and (b_min < a_max)


class viewport(mixin.capabilities):
    """The viewport offers a positionable window into a larger resolution
    pseudo-display, that also supports the concept of hotspots (which act like
    live displays).

    :param device: The device to project the enlarged pseudo-display viewport onto.
    :param width: The number of horizontal pixels.
    :type width: int
    :param height: The number of vertical pixels.
    :type height: int
    :param mode: The supported color model, one of ``"1"``, ``"RGB"`` or
        ``"RGBA"`` only.
    :type mode: str
    :param dither: By default, any color (other than black) will be `generally`
        treated as white when displayed on monochrome devices. However, this behaviour
        can be changed by adding ``dither=True`` and the image will be converted from RGB
        space into a 1-bit monochrome image where dithering is employed to differentiate
        colors at the expense of resolution.
    :type dither: bool
    """

    def __init__(self, device, width, height, mode=None, dither=False):
        self.capabilities(width, height, rotate=0, mode=mode or device.mode)
        if hasattr(device, "segment_mapper"):
            self.segment_mapper = device.segment_mapper
        self._device = device
        self._backing_image = Image.new(self.mode, self.size)
        self._position = (0, 0)
        self._hotspots = []
        self._dither = dither

    def display(self, image):
        assert image.mode == self.mode
        assert image.size == self.size

        self._backing_image.paste(image)
        self.refresh()

    def set_position(self, xy):
        self._position = xy
        self.refresh()

    def add_hotspot(self, hotspot, xy):
        """Add the hotspot at ``(x, y)``.

        The hotspot must fit inside the bounds of the virtual device. If
        it does not then an ``AssertError`` is raised.
        """
        (x, y) = xy
        assert 0 <= x <= self.width - hotspot.width
        assert 0 <= y <= self.height - hotspot.height

        # TODO: should it check to see whether hotspots overlap each other?
        # Is sensible to _allow_ them to overlap?
        self._hotspots.append((hotspot, xy))

    def remove_hotspot(self, hotspot, xy):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        self._hotspots.remove((hotspot, xy))
        eraser = Image.new(self.mode, hotspot.size)
        self._backing_image.paste(eraser, xy)

    def is_overlapping_viewport(self, hotspot, xy):
        """Checks to see if the hotspot at position ``(x, y)`` is (at least
        partially) visible according to the position of the viewport."""
        l1, t1, r1, b1 = calc_bounds(xy, hotspot)
        l2, t2, r2, b2 = calc_bounds(self._position, self._device)
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    def refresh(self):
        should_wait = False
        for hotspot, xy in self._hotspots:
            if hotspot.should_redraw() and self.is_overlapping_viewport(hotspot, xy):
                pool.add_task(hotspot.paste_into, self._backing_image, xy)
                should_wait = True

        if should_wait:
            pool.wait_completion()

        im = self._backing_image.crop(box=self._crop_box())
        if self._dither:
            im = im.convert(self._device.mode)

        self._device.display(im)

    def _crop_box(self):
        (left, top) = self._position
        right = left + self._device.width
        bottom = top + self._device.height

        assert 0 <= left <= right <= self.width
        assert 0 <= top <= bottom <= self.height

        return (left, top, right, bottom)


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
