from pitop.pulse import configuration

from pitopcommon.logger import PTLogger

from binascii import (
    hexlify,
    unhexlify
)
from tempfile import mkstemp
from os import (
    close,
    path,
    remove,
    rename,
    stat,
)
import serial
import signal
from struct import pack
from sys import exit
from threading import Thread
from time import sleep


_bitrate = 8
_continue_writing = False
_recording_thread = False
_thread_running = False
_exiting = False
_temp_file_path = ""

#######################
# INTERNAL OPERATIONS #
#######################


def __signal_handler(signal, frame):
    """INTERNAL. Handles signals from the OS."""

    global _exiting

    if _exiting is False:
        _exiting = True

        if _thread_running is True:
            stop()

    PTLogger.info("\nQuitting...")
    exit(0)


def __get_size(filename):
    """INTERNAL. Gets the size of a file."""

    file_stats = stat(filename)
    return file_stats.st_size


def __from_hex(value):
    """INTERNAL. Gets a bytearray from hex data."""

    return bytearray.fromhex(value)


def __space_separated_little_endian(integer_value, byte_len):
    """INTERNAL. Get an integer in format for WAV file header."""

    if byte_len <= 1:
        pack_type = '<B'
    elif byte_len <= 2:
        pack_type = '<H'
    elif byte_len <= 4:
        pack_type = '<I'
    elif byte_len <= 8:
        pack_type = '<Q'
    else:
        PTLogger.info("Value cannot be represented in 8 bytes - exiting")
        exit()

    hex_string = pack(pack_type, integer_value)
    temp = hexlify(hex_string).decode()
    return ' '.join([temp[i:i + 2] for i in range(0, len(temp), 2)])


def __init_header_information():
    """INTERNAL. Create a WAV file header."""

    RIFF = "52 49 46 46"
    WAVE = "57 41 56 45"
    fmt = "66 6d 74 20"
    DATA = "64 61 74 61"

    if configuration.microphone_sample_rate_is_22khz():
        capture_sample_rate = 22050
    else:
        capture_sample_rate = 16000

    # ChunkID
    header = __from_hex(RIFF)
    # ChunkSize - 4 bytes (to be changed depending on length of data...)
    header += __from_hex(__space_separated_little_endian(0, 4))
    # Format
    header += __from_hex(WAVE)
    # Subchunk1ID
    header += __from_hex(fmt)
    # Subchunk1Size (PCM = 16)
    header += __from_hex(__space_separated_little_endian(16, 4))
    # AudioFormat   (PCM = 1)
    header += __from_hex(__space_separated_little_endian(1, 2))
    header += __from_hex(__space_separated_little_endian(1, 2)
                         )                   # NumChannels
    # SampleRate
    header += __from_hex(__space_separated_little_endian(capture_sample_rate, 4))
    # ByteRate (Same as SampleRate due to 1 channel, 1 byte per sample)
    header += __from_hex(__space_separated_little_endian(capture_sample_rate, 4))
    # BlockAlign - (no. of bytes per sample)
    header += __from_hex(__space_separated_little_endian(1, 2))
    # BitsPerSample
    header += __from_hex(__space_separated_little_endian(_bitrate, 2))
    # Subchunk2ID
    header += __from_hex(DATA)
    # Subchunk2Size - 4 bytes (to be changed depending on length of data...)
    header += __from_hex(__space_separated_little_endian(0, 4))

    return header


def __update_header_in_file(file, position, value):
    """INTERNAL. Update the WAV header  """

    hex_value = __space_separated_little_endian(value, 4)
    data = unhexlify(''.join(hex_value.split()))

    file.seek(position)
    file.write(data)


def __finalise_wav_file(file_path):
    """INTERNAL. Update the WAV file header with the size of the data."""

    size_of_data = __get_size(file_path) - 44

    if size_of_data <= 0:
        PTLogger.info("Error: No data was recorded!")
        remove(file_path)
    else:
        with open(file_path, 'rb+') as file:

            PTLogger.debug("Updating header information...")

            __update_header_in_file(file, 4, size_of_data + 36)
            __update_header_in_file(file, 40, size_of_data)


def __thread_method():
    """INTERNAL. Thread method."""

    __record_audio()


def __record_audio():
    """INTERNAL. Open the serial port and capture audio data into a temp file."""

    global _temp_file_path

    temp_file_tuple = mkstemp()
    close(temp_file_tuple[0])
    _temp_file_path = temp_file_tuple[1]

    if path.exists('/dev/serial0'):

        PTLogger.debug("Opening serial device...")

        serial_device = serial.Serial(port='/dev/serial0', timeout=1, baudrate=250000,
                                      parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        serial_device_open = serial_device.isOpen()

        if serial_device_open is True:

            try:
                PTLogger.debug("Start recording")

                with open(_temp_file_path, 'wb') as file:

                    PTLogger.debug("WRITING: initial header information")
                    file.write(__init_header_information())

                    if serial_device.inWaiting():
                        PTLogger.debug(
                            "Flushing input and starting from scratch")
                        serial_device.flushInput()

                    PTLogger.debug("WRITING: wave data")

                    while _continue_writing:
                        while not serial_device.inWaiting():
                            sleep(0.01)

                        audio_output = serial_device.read(
                            serial_device.inWaiting())
                        bytes_to_write = bytearray()

                        for pcm_data_block in audio_output:

                            if _bitrate == 16:

                                pcm_data_int = 0
                                pcm_data_int = pcm_data_block
                                scaled_val = int((pcm_data_int * 32768) / 255)
                                bytes_to_write += __from_hex(
                                    __space_separated_little_endian(scaled_val, 2))

                            else:

                                pcm_data_int = pcm_data_block
                                bytes_to_write += __from_hex(
                                    __space_separated_little_endian(pcm_data_int, 1))

                        file.write(bytes_to_write)

                        sleep(0.1)

            finally:
                serial_device.close()

                __finalise_wav_file(_temp_file_path)

                PTLogger.debug("Finished Recording.")

        else:
            PTLogger.info("Error: Serial port failed to open")

    else:
        PTLogger.info(
            "Error: Could not find serial port - are you sure it's enabled?")


#######################
# EXTERNAL OPERATIONS #
#######################

def record():
    """Start recording on the pi-topPULSE microphone."""

    global _thread_running
    global _continue_writing
    global _recording_thread

    if not configuration.mcu_enabled():
        PTLogger.info("Error: pi-topPULSE is not initialised.")
        exit()

    if _thread_running is False:
        _thread_running = True
        _continue_writing = True
        _recording_thread = Thread(group=None, target=__thread_method)
        _recording_thread.start()
    else:
        PTLogger.info("Microphone is already recording!")


def is_recording():
    """Returns recording state of the pi-topPULSE microphone."""

    return _thread_running


def stop():
    """Stops recording audio"""

    global _thread_running
    global _continue_writing

    _continue_writing = False
    _recording_thread.join()
    _thread_running = False


def save(file_path, overwrite=False):
    """Saves recorded audio to a file."""

    global _temp_file_path

    if _thread_running is False:
        if _temp_file_path != "" and path.exists(_temp_file_path):
            if path.exists(file_path) is False or overwrite is True:

                if path.exists(file_path):
                    remove(file_path)

                rename(_temp_file_path, file_path)
                _temp_file_path = ""

            else:
                PTLogger.info("File already exists")
        else:
            PTLogger.info("No recorded audio data found")
    else:
        PTLogger.info("Microphone is still recording!")


def set_sample_rate_to_16khz():
    """Set the appropriate I2C bits to enable 16,000Hz recording on the microphone"""

    configuration.set_microphone_sample_rate_to_16khz()


def set_sample_rate_to_22khz():
    """Set the appropriate I2C bits to enable 22,050Hz recording on the microphone"""

    configuration.set_microphone_sample_rate_to_22khz()


def set_bit_rate_to_unsigned_8():
    """Set bitrate to device default"""

    global _bitrate
    _bitrate = 8


def set_bit_rate_to_signed_16():
    """Set bitrate to double that of device default by scaling the signal"""

    global _bitrate
    _bitrate = 16


#######################
# INITIALISATION      #
#######################

_signal = signal.signal(signal.SIGINT, __signal_handler)
