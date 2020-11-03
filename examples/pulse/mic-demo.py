#!/usr/bin/env python

"""
MIT License

Copyright (c) 2017 CEED Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from ptpulse import ledmatrix
from ptpulse import microphone
from ptpulse import configuration
from time import sleep


def set_bit_rate_to_unsigned_8():
    print("Setting bit rate to 8...")
    microphone.set_bit_rate_to_unsigned_8()


def set_bit_rate_to_signed_16():
    print("Setting bit rate to 16...")
    microphone.set_bit_rate_to_signed_16()


def set_sample_rate_to_16khz():
    print("Setting sample rate to 16KHz...")
    microphone.set_sample_rate_to_16khz()


def set_sample_rate_to_22khz():
    print("Setting sample rate to 22KHz...")
    microphone.set_sample_rate_to_22khz()


def pause(length):
    ledmatrix.off()
    sleep(length)


def record(record_time, output_file, pause_time=1):
    print("Recording audio for " + str(record_time) + "s...")
    ledmatrix.set_all(255, 0, 0)
    ledmatrix.show()
    microphone.record()
    sleep(record_time)
    microphone.stop()
    ledmatrix.off()
    microphone.save(output_file, True)
    print("Saved to " + output_file)
    print("")
    pause(pause_time)


set_sample_rate_to_22khz()
set_bit_rate_to_unsigned_8()
record(5, "/tmp/test22-8.wav")
set_bit_rate_to_signed_16()
record(5, "/tmp/test22-16.wav")

set_sample_rate_to_16khz()
set_bit_rate_to_unsigned_8()
record(5, "/tmp/test16-8.wav")
set_bit_rate_to_signed_16()
record(5, "/tmp/test16-16.wav")
