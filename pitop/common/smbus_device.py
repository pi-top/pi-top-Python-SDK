"""Wrapper for smbus for when standard I2C protocol is required, in contrast to
the less-than-standard I2C used on older devices."""

from pitop.common.logger import PTLogger
from pitop.common.bitwise_ops import get_bits, split_into_bytes, join_bytes
from smbus2 import SMBus


class SMBusDevice:

    def __init__(self, bus_number: int, device_address: int):
        self._bus_number = bus_number
        self._device_address = device_address
        self._bus = None

    def connect(self):
        PTLogger.debug(
            "I2C (SMBus): Connecting to address "
            + hex(self._device_address)
            + " on bus "
            + str(self._bus_number)
        )

        self._bus = SMBus(self._bus_number)

    def disconnect(self):
        PTLogger.debug("I2C (SMBus): Disconnecting...")
        self._bus.close()

    ####################
    # WRITE OPERATIONS #
    ####################
    def write_n_bytes(self, register_address: int, byte_list: list):
        """Base function to write to an I2C device."""
        PTLogger.debug(
            "I2C: Writing byte/s " +
            str(byte_list) + " to " + hex(register_address)
        )
        self._bus.write_i2c_block_data(
            self._device_address, register_address, byte_list)

    def write_byte(self, register_address: int, byte_value: int):
        if byte_value > 0xFF:
            PTLogger.warning(
                "Possible unintended overflow writing value to register "
                + hex(register_address)
            )
        self._bus.write_byte_data(
            self._device_address, register_address, byte_value)

    def write_word(self, register_address: int, word_value: int, little_endian: bool, signed: bool):
        bytes_to_write = split_into_bytes(
            word_value, 2, little_endian=little_endian, signed=signed)
        if bytes_to_write is None:
            PTLogger.error(f"Error splitting word into bytes list. Value: {word_value}")
            return

        self.write_n_bytes(register_address, bytes_to_write)

    ###################
    # READ OPERATIONS #
    ###################
    def _read_n_bytes(
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

        result_array = self._bus.read_i2c_block_data(
            self._device_address, register_address, number_of_bytes)

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
        return self._read_n_bytes(
            register_address, number_of_bytes, signed=False, little_endian=little_endian
        )

    def read_unsigned_byte(self, register_address: int):
        return self.read_n_unsigned_bytes(register_address, 1)

    def read_n_signed_bytes(
            self, register_address: int, number_of_bytes: int, little_endian=False
    ):
        return self._read_n_bytes(
            register_address, number_of_bytes, signed=True, little_endian=little_endian
        )

    def read_signed_byte(self, register_address: int):
        return self.read_n_signed_bytes(register_address, 1)

    def read_unsigned_word(self, register_address: int, little_endian=False):
        return self._read_n_bytes(register_address, 2, little_endian=little_endian)

    def read_signed_word(self, register_address: int, little_endian=False):
        return self._read_n_bytes(
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
