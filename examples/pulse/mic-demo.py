from pitop.pulse import (
    ledmatrix,
    microphone
)

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
