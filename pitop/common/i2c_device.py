from pitop.common.logger import PTLogger
from pitop.common.lock import PTLock
from pitop.common.bitwise_ops import get_bits, split_into_bytes, join_bytes

from io import open as iopen
from fcntl import ioctl
from time import sleep


class I2CDevice:
    I2C_SLAVE = 0x0703

    def __init__(self, device_path: str, device_address: int):
        self._device_path = device_path
        self._device_address = device_address

        self._post_read_delay = 0.020
        self._post_write_delay = 0.020

        self._lock = PTLock(f"i2c_{device_address:#0{4}x}")

        self._read_device = None
        self._write_device = None

    def set_delays(self, read_delay: float, write_delay: float):
        self._post_read_delay = read_delay
        self._post_write_delay = write_delay

    def connect(self, read_test=True):
        PTLogger.debug(
            "I2C: Connecting to address "
            + hex(self._device_address)
            + " on "
            + self._device_path
        )

        self._read_device = iopen(self._device_path, "rb", buffering=0)
        self._write_device = iopen(self._device_path, "wb", buffering=0)

        ioctl(self._read_device, self.I2C_SLAVE, self._device_address)
        ioctl(self._write_device, self.I2C_SLAVE, self._device_address)

        if read_test is True:
            PTLogger.debug("I2C: Test read 1 byte")
            self._read_device.read(1)
            PTLogger.debug("I2C: OK")

    def disconnect(self):
        PTLogger.debug("I2C: Disconnecting...")

        if self._write_device is not None:
            self._write_device.close()

        if self._read_device is not None:
            self._read_device.close()

    ####################
    # WRITE OPERATIONS #
    ####################
    def write_n_bytes(self, register_address: int, byte_list: list):
        """Base function to write to an I2C device."""
        PTLogger.debug(
            "I2C: Writing byte/s " +
            str(byte_list) + " to " + hex(register_address)
        )
        self.__run_transaction([register_address] + byte_list, 0)

    def write_byte(self, register_address: int, byte_value: int):
        if byte_value > 0xFF:
            PTLogger.warning(
                "Possible unintended overflow writing value to register "
                + hex(register_address)
            )

        self.write_n_bytes(register_address, [byte_value & 0xFF])

    def write_word(self, register_address: int, word_value: int, little_endian: bool = False, signed: bool = False):
        word_to_write = split_into_bytes(
            word_value, 2, little_endian=little_endian, signed=signed)
        if word_to_write is None:
            PTLogger.error(f"Error splitting word into bytes list. Value: {word_value}")
        else:
            self.write_n_bytes(register_address, word_to_write)

    ###################
    # READ OPERATIONS #
    ###################
    def __read_n_bytes(
        self,
        register_address: int,
        number_of_bytes: int,
        signed: bool = False,
        little_endian: bool = False,
    ):
        """Base function to read from an I2C device.

        :param register_address: Register address to target for reading
        :param number_of_bytes: Number of bytes to attempt to read from register address
        :param signed: Indicates whether or not the value could potentially have a negative value, and is therefore
        represented with a signed number representation
        :param little_endian: Indicates whether the data to be read is in little-endian byte-order
        :return: result: The response from the read attempt via I2C
        """

        # Read from device
        result_array = self.__run_transaction(
            [register_address],
            number_of_bytes
        )

        # Check response length is correct
        if len(result_array) != number_of_bytes:
            return None

        # Invert byte ordering, if appropriate
        if little_endian:
            result_array.reverse()

        # Convert array into integer
        result = join_bytes(result_array)

        # Process signed number if appropriate
        if signed:
            if result & (1 << ((8 * number_of_bytes) - 1)):
                result = -(1 << (8 * number_of_bytes)) + result

        PTLogger.debug(
            "I2C: Read " + str(number_of_bytes) + " bytes from " + hex(register_address) + " (" + (
                "Signed," if signed else "Unsigned,") + ("LE" if little_endian else "BE") + ")"
        )
        PTLogger.debug(str(result_array) + " : " + str(result))

        return result

    # HELPER FUNCTIONS TO SIMPLIFY EXTERNAL READABILITY
    def read_n_unsigned_bytes(
        self, register_address: int, number_of_bytes: int, little_endian=False
    ):
        return self.__read_n_bytes(
            register_address, number_of_bytes, signed=False, little_endian=little_endian
        )

    def read_unsigned_byte(self, register_address: int):
        return self.read_n_unsigned_bytes(register_address, 1)

    def read_n_signed_bytes(
        self, register_address: int, number_of_bytes: int, little_endian=False
    ):
        return self.__read_n_bytes(
            register_address, number_of_bytes, signed=True, little_endian=little_endian
        )

    def read_signed_byte(self, register_address: int):
        return self.read_n_signed_bytes(register_address, 1)

    def read_unsigned_word(self, register_address: int, little_endian=False):
        return self.__read_n_bytes(register_address, 2, little_endian=little_endian)

    def read_signed_word(self, register_address: int, little_endian=False):
        return self.__read_n_bytes(
            register_address, 2, signed=True, little_endian=little_endian
        )

    # HELPER FUNCTIONS TO EXTRACT BITS FROM A READ
    def read_bits_from_byte_at_address(self, bits_to_read: int, addr_to_read: int):
        return self.read_bits_from_n_bytes_at_address(bits_to_read, addr_to_read, 1)

    def read_bits_from_n_bytes_at_address(
        self, bits_to_read: int, addr_to_read: int, no_of_bytes_to_read: int = 1
    ):
        return get_bits(
            bits_to_read, self.read_n_unsigned_bytes(
                addr_to_read, no_of_bytes_to_read)
        )

    ####################
    # INTERNAL METHODS #
    ####################
    def __run_transaction(self, listin: list, expected_read_length: int):
        with self._lock:
            self.__write_data(bytearray(listin))
            return self.__read_data(expected_read_length)

    def __write_data(self, data: bytearray):
        data = bytes(data)
        self._write_device.write(data)
        sleep(self._post_write_delay)

    def __read_data(self, expected_output_size: int):
        if expected_output_size == 0:
            return 0

        result_array = list()
        data = self._read_device.read(expected_output_size)
        sleep(self._post_read_delay)

        if len(data) != 0:
            for n in data:
                if data is str:
                    result_array.append(ord(n))
                else:
                    result_array.append(n)

        return result_array
