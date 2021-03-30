#!/usr/bin/env python
# coding: utf-8

# Copyright 2011 Álvaro Justen [alvarojusten at gmail dot com]
# License: GPL <http://www.gnu.org/copyleft/gpl.html>

from PIL import ImageDraw, ImageFont


class ImageTextFunctions(object):
    def get_font_size(text, font_filename, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = ImageTextFunctions.get_text_size(font_filename, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" %
                             text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = ImageTextFunctions.get_text_size(font_filename, font_size, text)

    def get_text_size(font_filename, font_size, text):
        font = ImageFont.truetype(font_filename, font_size)
        return font.getsize(text)

    def write_text(image, xy, text, font_filename, font_size='fill',
                   color=(0, 0, 0), max_width=None, max_height=None):

        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = ImageTextFunctions.get_font_size(
                text,
                font_filename,
                max_width,
                max_height
            )

        font = ImageFont.truetype(
            font_filename,
            font_size
        )

        text_size = ImageTextFunctions.get_text_size(
            image,
            font_filename,
            font_size,
            text
        )

        x, y = xy
        if x == 'center':
            x = (image.size[0] - text_size[0]) / 2
        if y == 'center':
            y = (image.size[1] - text_size[1]) / 2

        ImageDraw.Draw(image).text(
            (x, y),
            text,
            font=font,
            fill=color
        )
        return text_size
