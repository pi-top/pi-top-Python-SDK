import pitop.utils.bitwise_ops as bitwise
from unittest import TestCase
from parameterized import parameterized
from sys import modules
from unittest.mock import Mock

mock_logger = modules["pitop.utils.logger"] = Mock()


class BitwiseOpsTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    """
    split_into_bytes tests
    Tested:
        Integer with number of bytes not set
        Integer with chosen big enough number of bytes set
        Integer with number of bytes set to a value too small for the integer
        Zero value with number of bytes not set
    """

    @parameterized.expand(
        [
            [18, -1, [18]],
            [18, 5, [0, 0, 0, 0, 18]],
            [256, 5, [0, 0, 0, 1, 0]],
            [65536, 3, [1, 0, 0]],
            [18, 0, None],
            [256, -1, [1, 0]],
            [256, 2, [1, 0]],
            [256, 5, [0, 0, 0, 1, 0]],
            [256, 1, None],
            [0, -1, []],
        ]
    )
    def test_split_into_bytes_unsigned(self, data: int, no_of_bytes: int, expected_list):

        test_bytes_list = bitwise.split_into_bytes(data, no_of_bytes)
        self.assertEqual(expected_list, test_bytes_list)

    @parameterized.expand(
        [
            [1, 2, [0, 1]],
            [-1, 4, [255, 255, 255, 255]],
            [-600000, 4, [255, 246, 216, 64]],
            [-600000, 2, None],
            [-200, 4, [255, 255, 255, 56]],
            [32767, 2, [127, 255]],
            [32768, 2, None],
            [-32768, 2, [128, 0]],
            [-32769, 2, None],
        ]
    )
    def test_split_into_bytes_signed(self, data: int, no_of_bytes: int, expected_list):

        test_bytes_list = bitwise.split_into_bytes(
            data, no_of_bytes, signed=True)
        self.assertEqual(expected_list, test_bytes_list)

    """
    join_bytes tests
    Tested:
        Integer list value with extra zero padding
        Single value integer list
        Integer list with multiple values
        Integer list with values written in hex form
        Empty list

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)
        List with non integer values
    """

    @parameterized.expand(
        [
            [[0, 0, 0, 1, 0], 256],
            [[18], 18],
            [[1, 1, 1, 1, 1], 4311810305],
            [[0x1F, 0x02], 7938],
            [[0xF1, 0xFF], 61951],
            [[0, 0, 0x00, 1, 0], 256],
            [[], 0],
        ]
    )
    def test_join_bytes(self, byte_list, expected_value):
        test_value = bitwise.join_bytes(byte_list)
        self.assertEqual(expected_value, test_value)

    """
    flip_bits tests
    Tested:
        Default number of bytes with valid input
        Set number of bytes with valid input
        Use large value with number of bytes set
        Value with extra zero padding with default number of bytes
        Value with extra zero padding with number of bytes set
        number of bytes set to a value too small

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)

    """

    @parameterized.expand(
        [
            [0x1010, -1, 0xFEF],
            [0x14, -1, 0xB],
            [0x00001, -1, 0x0],
            [0x00001, 3, 0xFFFFFE],
            [0xA6, 1, 0x59],
            [0xA6, 2, 0xFF59],
            [0xA6, 3, 0xFFFF59],
            [0x3BA6, -1, 0x459],
            [0x3BA6, 2, 0xC459],
            [0x112233445566, 6, 0xEEDDCCBBAA99],
            [0xC3, -1, 0x3C],
            [0x125AC3, 2, 0xDA53C],
        ]
    )
    def test_flip_bits(self, bitwise_data, num_of_bytes, expected_value):
        test_value = bitwise.flip_bits(bitwise_data, num_of_bytes)
        self.assertEqual(expected_value, test_value)

    """
    get_bits tests
    Tested:
        Same length bitmask as the data
        Zero value bitmask with zero value data
        Zero value bitmask with non-zero value data
        Smaller length bitmask to data
        Larger length bitmask to data

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)

    """

    @parameterized.expand(
        [
            [0x110, 0x1110, 0x110],
            [0x110, 0x01110001, 0x0],
            [0x11000, 0x01110001, 0x10000],
            [0x100000000000, 0x01110001, 0x00],
            [0x01110001, 0x01110001, 0x01110001],
            [0x18, 0x71, 0x10],
            [0x30, 0x71, 0x30],
            [0x00, 0x01, 0x00],
            [0x00, 0x00, 0x00],
        ]
    )
    def test_get_bits(self, bitmask_to_get, bitwise_data, expected_value):
        test_value = bitwise.get_bits(bitmask_to_get, bitwise_data)
        self.assertEqual(expected_value, test_value)

    """
    ignore_bits tests
    Tested:
        Setting different bits to low from same data
        Different length bitmasks to data
        Zero value case with zero value data

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)
        Longer length bitmask to data
        Zero value case with non-zero value data
    """

    @parameterized.expand(
        [
            [0x100, 0x1110, 0x1010],
            [0x110, 0x01110001, 0x01110001],
            [0x00110000, 0x01110001, 0x01000001],
            [0x10000000, 0x01110001, 0x01110001],
            [0x01110001, 0x01110001, 0x0],
            [0x18, 0x71, 0x61],
            [0x30, 0x71, 0x41],
            [0x00, 0x00, 0x00],
            [0x11, 0x24167399, 0x24167388],
            [15, 255, 240],
            [0xFF, 0xFF, 0],
            [0xF0, 0xF0F0, 0xF000],
        ]
    )
    def test_ignore_bits(self, bitmask_to_ignore, bitwise_data, expected_value):
        test_value = bitwise.ignore_bits(bitmask_to_ignore, bitwise_data)
        self.assertEqual(expected_value, test_value)

    """
    set_bits_high tests
    Tested:
        Setting different bits to high from same data
        Different length bitmasks to data
        Zero value case with zero value data
        Longer length bitmask to data

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)
        Zero value case with non-zero value data
    """

    @parameterized.expand(
        [
            [0x100, 0x1010, 0x1110],
            [0x01110001, 0x01110001, 0x01110001],
            [0x0000000, 0x01110001, 0x01110001],
            [0x00000011, 0x01110001, 0x01110011],
            [0x1000000000011, 0x01110001, 0x1000001110011],
            [0x18, 0x71, 0x79],
            [0x30, 0x71, 0x71],
            [0x00, 0x00, 0x00],
        ]
    )
    def test_set_bits_high(self, bits_to_raise, bitwise_data, expected_value):
        test_value = bitwise.set_bits_high(bits_to_raise, bitwise_data)
        self.assertEqual(expected_value, test_value)

    """
    bitmask_is_on tests
    Tested:
        Same value checked against itself
        Different length bitmask check against data
        Zero value case with zero value data
        Partial matching check against data
        Zero value bitmask against non zero data

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)
        Zero value case with non-zero value data
    """

    @parameterized.expand(
        [
            [0x100, 0x100, True],
            [0x100, 0x010, False],
            [0x01110001, 0x01110001, True],
            [0x01110011, 0x01110001, False],
            [0x0000000, 0x01110001, True],
            [0x1, 0x01110001, True],
            [0x01110001, 0x1, False],
            [0x18, 0x71, False],
            [0x30, 0x71, True],
            [0x71, 0x71, True],
            [0x00, 0x00, True],
        ]
    )
    def test_bitmask_is_on(self, bitmask_to_check, bitwise_data, expected_bool):
        test_value = bitwise.bitmask_is_on(bitmask_to_check, bitwise_data)
        self.assertEqual(expected_bool, test_value)

    """
    all_bits_are_on tests
    Tested:
        Empty list against non empty data
        Different bit length values in list checked against data
        List with one Not matching value

    Not tested cases:
    (These test cases are considered edge cases or low priority based on the intended use)
        Empty list against empty data
        List of multiple non-matching values
    """

    @parameterized.expand(
        [
            [[0x00, 0x101, 0x101, 0x001], 0x101, True],
            [[0x01, 0x10001, 0x110001], 0x01110001, True],
            [[0x01, 0x10101, 0x110001], 0x01110001, False],
            [[0x30, 0x01, 0x70], 0x71, True],
            [[0x01, 0x18], 0x71, False],
            [[], 0x01110001, True],
        ]
    )
    def test_all_bits_are_on(
        self, bits_to_check: list, bitwise_data: int, expected_bool
    ):
        test_list = bitwise.all_bits_are_on(bits_to_check, bitwise_data)
        self.assertEqual(expected_bool, test_list)
