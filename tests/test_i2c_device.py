from unittest import TestCase
from unittest.mock import Mock, patch

from parameterized import parameterized


class I2CDeviceTestCase(TestCase):
    _dummy_device_path = "test_device_path"
    _dummy_device_address = 0x99
    _dummy_register = 0x77

    def setUp(self):
        self.iopen_patch = patch("pitop.common.i2c_device.iopen")
        self.ioctl_patch = patch("pitop.common.i2c_device.ioctl")
        self.sleep_patch = patch("pitop.common.i2c_device.sleep")
        self.ptlock_patch = patch("pitop.common.i2c_device.PTLock")

        self.iopen_mock = self.iopen_patch.start()
        self.ioctl_mock = self.ioctl_patch.start()
        self.sleep_mock = self.sleep_patch.start()
        self.ptlock_mock = self.ptlock_patch.start()

        self.addCleanup(self.iopen_patch.stop)
        self.addCleanup(self.ioctl_patch.stop)
        self.addCleanup(self.sleep_patch.stop)
        self.addCleanup(self.ptlock_patch.stop)

        from pitop.common.i2c_device import I2CDevice  # noqa: E402

        self._i2c_device = I2CDevice(
            self._dummy_device_path, self._dummy_device_address
        )

        self._mock_read_device = Mock()
        self._mock_write_device = Mock()
        self._ptlock_mock = Mock(__enter__=Mock(), __exit__=Mock())

        self._i2c_device._lock = self._ptlock_mock

        self.iopen_mock.side_effect = [
            self._mock_read_device,
            self._mock_write_device,
        ]

    def test_initialisation_creates_lock_file(self):
        self.ptlock_mock.assert_called_once_with(
            f"i2c_{hex(self._dummy_device_address)}"
        )

    def test_connect_opens_device_file_for_rw(self):
        self._i2c_device.connect(read_test=True)

        self.iopen_mock.assert_any_call(self._dummy_device_path, "rb", buffering=0)
        self.iopen_mock.assert_any_call(self._dummy_device_path, "wb", buffering=0)

        self.ioctl_mock.assert_any_call(
            self._mock_read_device,
            self._i2c_device.I2C_SLAVE,
            self._dummy_device_address,
        )
        self.ioctl_mock.assert_any_call(
            self._mock_write_device,
            self._i2c_device.I2C_SLAVE,
            self._dummy_device_address,
        )

    def test_connect_does_not_run_read_test(self):
        self._i2c_device.connect(read_test=False)

        self._mock_read_device.read.assert_not_called()

    def test_connect_runs_read_test(self):
        self._i2c_device.connect(read_test=True)

        self._mock_read_device.read.assert_called_once_with(1)

    def test_disconnect_closes_devices(self):
        self._i2c_device.connect(read_test=False)
        self._i2c_device.disconnect()

        self._mock_read_device.close.assert_called_once()
        self._mock_write_device.close.assert_called_once()

    def test_write_n_bytes_writes_data_to_device(self):
        test_data = [0x01, 0x02, 0x03]

        self._i2c_device.connect(read_test=False)
        self._i2c_device.write_n_bytes(self._dummy_register, test_data)
        self._i2c_device.disconnect()

        self._mock_write_device.write.assert_called_once_with(
            bytes(bytearray([self._dummy_register]) + bytearray(test_data))
        )

    def test_write_n_bytes_sleeps_after_write(self):
        self._i2c_device.connect(read_test=False)
        self._i2c_device.write_n_bytes(self._dummy_register, [0x01, 0x02, 0x03])
        self._i2c_device.disconnect()

        self.sleep_mock.assert_called_once_with(self._i2c_device._post_write_delay)

    @parameterized.expand([[[0x01], 0x01], [[0x08], 0x08], [[0xAF], 0xAF]])
    def test_read_unsigned_byte(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_unsigned_byte(self._dummy_register)
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand([[[0x01, 0x02], None], [[0x08, 0x09, 0x1, 0x04], None]])
    def test_read_unsigned_byte__incorrect_input(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_unsigned_byte(self._dummy_register)
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand([[[0x01], 0x01], [[0x08], 0x08], [[0x10], 0x10]])
    def test_read_signed_byte(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_signed_byte(self._dummy_register)
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01, 0x02], 0x0201],
            [[0x01, 0x08], 0x0801],
            [[0x01, 0x03], 0x0301],
            [[0x03, 0x04], 0x0403],
            [[0x07, 0x08], 0x0807],
        ]
    )
    def test_read_unsigned_word(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_unsigned_word(
            self._dummy_register, little_endian=True
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01], None],
            [[0x01, 0x02, 0x01, 0x08], None],
            [[0x01, 0x03, 0x03, 0x04], None],
        ]
    )
    def test_read_unsigned_word__incorrect_input(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_unsigned_word(
            self._dummy_register, little_endian=True
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01, 0x02], 0x0102],
            [[0x01, 0x08], 0x0108],
            [[0x01, 0x03], 0x0103],
            [[0x03, 0x04], 0x0304],
            [[0x07, 0x08], 0x0708],
        ]
    )
    def test_read_unsigned_word__big_endian(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_unsigned_word(
            self._dummy_register, little_endian=False
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01, 0x02], 0x0201],
            [[0x01, 0x08], 0x0801],
            [[0x01, 0x03], 0x0301],
            [[0x03, 0x04], 0x0403],
            [[0x07, 0x08], 0x0807],
        ]
    )
    def test_read_signed_word(self, read_value, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_signed_word(
            self._dummy_register, little_endian=True
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01], 1, 0x01],
            [[0x01, 0x08], 2, 0x0801],
            [[0x01, 0x02, 0x03], 3, 0x030201],
            [[0x01, 0x02, 0x03, 0x04], 4, 0x04030201],
            [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0807060504030201],
        ]
    )
    def test_read_n_unsigned_bytes(self, read_value, no_bytes_to_read, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_n_unsigned_bytes(
            self._dummy_register, no_bytes_to_read, little_endian=True
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01], 1, 0x01],
            [[0x01, 0x08], 2, 0x0801],
            [[0x01, 0x02, 0x03], 3, 0x030201],
            [[0x01, 0x02, 0x03, 0x04], 4, 0x04030201],
            [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0807060504030201],
        ]
    )
    def test_read_n_signed_bytes(self, read_value, no_bytes_to_read, expected_value):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_n_signed_bytes(
            self._dummy_register, no_bytes_to_read, little_endian=True
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    @parameterized.expand(
        [
            [[0x01], 1, 0x01],
            [[0x01, 0x08], 2, 0x0108],
            [[0x01, 0x02, 0x03], 3, 0x010203],
            [[0x01, 0x02, 0x03, 0x04], 4, 0x01020304],
            [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0102030405060708],
        ]
    )
    def test_read_n_unsigned_bytes__big_endian(
        self, read_value, no_bytes_to_read, expected_value
    ):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_n_unsigned_bytes(
            self._dummy_register, no_bytes_to_read, little_endian=False
        )
        self._i2c_device.disconnect()

        self.assertEqual(expected_value, read_value)

    def test_write_n_bytes_acquires_and_releases_lock(self):
        test_data = [0x01, 0x02, 0x03]

        self._i2c_device.connect(read_test=False)
        self._i2c_device.write_n_bytes(self._dummy_register, test_data)
        self._i2c_device.disconnect()

        self._ptlock_mock.__enter__.assert_called_once()
        self._ptlock_mock.__exit__.assert_called_once()

    def test_no_transaction_leaves_lock_alone(self):
        self._i2c_device.connect(read_test=False)
        self._i2c_device.disconnect()

        self._ptlock_mock.__enter__.assert_not_called()
        self._ptlock_mock.__exit__.assert_not_called()

    @parameterized.expand([[[0x01], 1, 0x01]])
    def test_read_n_unsigned_bytes_acquires_and_releases_lock(
        self, read_value, no_bytes_to_read, expected_value
    ):
        self._mock_read_device.read.return_value = read_value
        self._i2c_device.connect(read_test=False)
        read_value = self._i2c_device.read_n_unsigned_bytes(
            self._dummy_register, no_bytes_to_read, little_endian=True
        )
        self._i2c_device.disconnect()

        self._ptlock_mock.__enter__.assert_called_once()
        self._ptlock_mock.__exit__.assert_called_once()
