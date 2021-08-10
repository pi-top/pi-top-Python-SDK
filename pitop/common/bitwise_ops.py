from math import ceil
from pitop.common.logger import PTLogger


def split_into_bytes(data: int, no_of_bytes: int = -1, little_endian: bool = False, signed: bool = False):
    """This function will split a given integer into a integer list
    representing the bytes to be split;

    :param data: A integer that represents the value of the bytes to be split
    :param no_of_bytes: The number of bytes the integer to be converted into. If the
     no_of_bytes is too small the method returns None.
    :return: A integer list representing a bytes list version of the given integer
    """

    byteorder_indicator = "little" if little_endian is True else "big"

    if no_of_bytes == -1:
        no_of_bytes = ceil(data / 255)
    try:
        byte_string = data.to_bytes(
            no_of_bytes, byteorder=byteorder_indicator, signed=signed)
    except OverflowError as e:
        PTLogger.error(e)
        return None

    return [
        i
        for i in bytearray(byte_string)
    ]


def join_bytes(byte_list: list, little_endian: bool = False, signed: bool = False):
    """This function will return an integer representing the `byte_list`;

    :param byte_list: A integer list representing a list of bytes
    :return: A integer representing the `byte_list`
    """
    return int.from_bytes(
        byte_list,
        byteorder="little" if little_endian is True else "big",
        signed=signed
    )


def get_bits(bitmask_to_get: int, bitwise_data: int):
    """This function will return the integer value represented by the bits that
    are high in `bitmask_to_get` from the bits that represent the integer
    value, `bitwise_data`.

    :param bitmask_to_get: A integer representing the bits you want to get from `bitwise_data`
    :param bitwise_data: A integer representing the data which to extract the bits out of
    :return: A integer representing bits extracted from `bitwise_data`
    """
    return bitmask_to_get & bitwise_data


def to_bits(int_to_convert: int):
    """This function will convert a integer into a binary string without a
    prefix (e.g. '0b');

    :param int_to_convert: A integer to convert into a binary string
    :return: A binary string representing the given integer
    """
    return bin(int_to_convert)[2:]


def from_bits(bin_str: str):
    """This function will convert a binary string (with or without prefix) into
    a integer;

    :param bin_str: A binary string to convert into integer
    :return: A integer representing the given binary string
    """
    return int(bin_str, 2)


def pad_bits(bin_str: str, no_of_bytes: int):
    """This function will 'left zero pad' `bin_str`, if necessary, to ensure
    that it matches length `num_of_bytes`;

    :param bin_str: A binary string which will be padded with '0's if necessary
    :param no_of_bytes: The number of bytes to determine the byte size of the return value
    :return: A string representing bin_str with or without padding
    """
    difference = (no_of_bytes * 8) - len(bin_str)
    if difference <= 0:
        return bin_str
    else:
        padding = "0" * difference
        return padding + bin_str


def flip_bin_string(bin_str: str):
    """This function will flip(invert) each of the bits in a given binary
    string without prefix. i.e. "0" becomes "1" and vice versa;

    :param bin_str: A binary string without prefix to flip
    :return: A binary data represented as string
    """
    flipped_bin_str = ""
    for bit in bin_str:
        flipped_bin_str += str(1 - int(bit))
    return flipped_bin_str


def flip_bits(bitwise_data: int, no_of_bytes: int = -1):
    """This function will flip(invert) the bits of `bitwise_data` and
    `num_of_bytes` allows you to choose the byte size of the value returned.
    This may have padding based on the value of `no_of_bytes`;

    :param bitwise_data: A integer representing the bits to flip
    :param no_of_bytes: A integer to set the number of bytes of the returned value
    :return: A integer representing `bitwise_data` with its bits flipped.
    """
    bin_string_of_data = to_bits(bitwise_data)

    if no_of_bytes <= 0:
        value_to_flip = bin_string_of_data
    else:
        value_to_flip = pad_bits(bin_string_of_data, no_of_bytes)

    flipped_bin_string = flip_bin_string(value_to_flip)
    return from_bits(flipped_bin_string)


def ignore_bits(bitmask_to_ignore: int, bitwise_data: int):
    """This function will set the bits high in `bitmask_to_ignore` low in
    `bitwise_data`;

    :param bitmask_to_ignore: A integer representing the bits you want to ignore
     from `bitwise_data`
    :param bitwise_data: A integer representing the data from which to ignore bits out of
    :return: A integer representing `bitwise_data` with the `bitmask_to_ignore` bits set
     to low
    """
    byte_size_of_data = ceil(bitwise_data.bit_length() / 8)
    return get_bits(flip_bits(bitmask_to_ignore, byte_size_of_data), bitwise_data)


def set_bits_low(bits_to_set_low: int, bitwise_data: int):
    """This function will set bits low based on `bits_to_set_low` in
    `bitwise_data`;

    :param bits_to_set_low: A integer representing the bits to set low in `bitwise_data`
    :param bitwise_data: A integer representing the data from which to set bits low out of
    :return: A integer representing `bitwise_data` with bits set low based on `bits_to_set_low`
    """
    return ignore_bits(bits_to_set_low, bitwise_data)


def set_bits_high(bits_to_set_high: int, bitwise_data: int):
    """This function will set bits high based on `bits_to_set_high` in
    `bitwise_data`;

    :param bits_to_set_high: A integer representing the bits to set high in `bitwise_data`
    :param bitwise_data: A integer representing the data from which to set bits high out of
    :return: A integer representing `bitwise_data` with bits set high based on `bits_to_set_high`
    """
    return bits_to_set_high | bitwise_data


def bitmask_is_on(bitmask_to_check: int, bitwise_data: int):
    """This function will check if bits are high in `bitwise_data` against bits
    that are high in `bitmask_to_check` and return True or False based on that;

    :param bitmask_to_check: A integer representing the bits to check in `bitwise_data`
    :param bitwise_data: A integer representing the data to check bits in
    :return: A boolean returns True only if the bits high in `bitmask_to_check`
     are high in `bitwise_data`
    """
    return all_bits_are_on([bitmask_to_check], bitwise_data)


def all_bits_are_on(bits_to_check: list, bitwise_data: int):
    """This function will determine if particular bits are high in some bitwise
    data.

    :param bits_to_check: A list of bit values to check for. Each value can either be an
     individual bit representation or it can be a 'summed' value which represents OR'd bits
      (e.g. ['0001 0000', '0000 0010' ] or ['0001 0010'])
    :param bitwise_data: The data to be checked
    :return: Boolean representing whether all the bits in
     `bits_to_check` are high in `bitwise_data`
    """
    summed_bits = 0
    for bit_to_check in bits_to_check:
        summed_bits = summed_bits | bit_to_check
    processed_bits = get_bits(summed_bits, bitwise_data)
    return processed_bits == summed_bits
