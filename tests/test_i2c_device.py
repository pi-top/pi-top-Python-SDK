from unittest.mock import Mock, patch

import pytest

_dummy_device_path = "test_device_path"
_dummy_device_address = 0x99
_dummy_register = 0x77


@pytest.fixture
def setup_mocks():
    iopen_patch = patch("pitop.common.i2c_device.iopen")
    ioctl_patch = patch("pitop.common.i2c_device.ioctl")
    sleep_patch = patch("pitop.common.i2c_device.sleep")
    ptlock_patch = patch("pitop.common.i2c_device.PTLock")

    iopen_mock = iopen_patch.start()
    ioctl_mock = ioctl_patch.start()
    sleep_mock = sleep_patch.start()
    ptlock_mock = ptlock_patch.start()

    from pitop.common.i2c_device import I2CDevice  # noqa: E402

    i2c_device = I2CDevice(_dummy_device_path, _dummy_device_address)

    ptlock_mock.assert_called_once_with(f"i2c_{hex(_dummy_device_address)}")

    mock_read_device = Mock()
    _mock_write_device = Mock()
    ptlock_mock = Mock(__enter__=Mock(), __exit__=Mock())

    i2c_device._lock = ptlock_mock

    iopen_mock.side_effect = [
        mock_read_device,
        _mock_write_device,
    ]

    yield {
        "ptlock_mock": ptlock_mock,
        "i2c_device": i2c_device,
        "iopen_mock": iopen_mock,
        "mock_read_device": mock_read_device,
        "mock_write_device": _mock_write_device,
        "sleep_mock": sleep_mock,
        "ioctl_mock": ioctl_mock,
    }

    iopen_patch.stop()
    ioctl_patch.stop()
    sleep_patch.stop()
    ptlock_patch.stop()


def test_connect_opens_device_file_for_rw(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    iopen_mock = setup_mocks.get("iopen_mock")
    ioctl_mock = setup_mocks.get("ioctl_mock")
    mock_read_device = setup_mocks.get("mock_read_device")
    _mock_write_device = setup_mocks.get("mock_write_device")

    i2c_device.connect(read_test=True)

    iopen_mock.assert_any_call(_dummy_device_path, "rb", buffering=0)
    iopen_mock.assert_any_call(_dummy_device_path, "wb", buffering=0)

    ioctl_mock.assert_any_call(
        mock_read_device,
        i2c_device.I2C_SLAVE,
        _dummy_device_address,
    )
    ioctl_mock.assert_any_call(
        _mock_write_device,
        i2c_device.I2C_SLAVE,
        _dummy_device_address,
    )


def test_connect_does_not_run_read_test(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    i2c_device.connect(read_test=False)

    mock_read_device.read.assert_not_called()


def test_connect_runs_read_test(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    i2c_device.connect(read_test=True)

    mock_read_device.read.assert_called_once_with(1)


def test_disconnect_closes_devices(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")
    _mock_write_device = setup_mocks.get("mock_write_device")

    i2c_device.connect(read_test=False)
    i2c_device.disconnect()

    mock_read_device.close.assert_called_once()
    _mock_write_device.close.assert_called_once()


def test_write_n_bytes_writes_data_to_device(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    _mock_write_device = setup_mocks.get("mock_write_device")

    test_data = [0x01, 0x02, 0x03]

    i2c_device.connect(read_test=False)
    i2c_device.write_n_bytes(_dummy_register, test_data)
    i2c_device.disconnect()

    _mock_write_device.write.assert_called_once_with(
        bytes(bytearray([_dummy_register]) + bytearray(test_data))
    )


def test_write_n_bytes_sleeps_after_write(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    sleep_mock = setup_mocks.get("sleep_mock")

    i2c_device.connect(read_test=False)
    i2c_device.write_n_bytes(_dummy_register, [0x01, 0x02, 0x03])
    i2c_device.disconnect()

    sleep_mock.assert_called_once_with(i2c_device._post_write_delay)


@pytest.mark.parametrize(
    "read_value,expected_value", [[[0x01], 0x01], [[0x08], 0x08], [[0xAF], 0xAF]]
)
def test_read_unsigned_byte(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_unsigned_byte(_dummy_register)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value", [[[0x01, 0x02], None], [[0x08, 0x09, 0x1, 0x04], None]]
)
def test_read_unsigned_byte__incorrect_input(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_unsigned_byte(_dummy_register)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value", [[[0x01], 0x01], [[0x08], 0x08], [[0x10], 0x10]]
)
def test_read_signed_byte(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_signed_byte(_dummy_register)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value",
    [
        [[0x01, 0x02], 0x0201],
        [[0x01, 0x08], 0x0801],
        [[0x01, 0x03], 0x0301],
        [[0x03, 0x04], 0x0403],
        [[0x07, 0x08], 0x0807],
    ],
)
def test_read_unsigned_word(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_unsigned_word(_dummy_register, little_endian=True)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value",
    [
        [[0x01], None],
        [[0x01, 0x02, 0x01, 0x08], None],
        [[0x01, 0x03, 0x03, 0x04], None],
    ],
)
def test_read_unsigned_word__incorrect_input(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_unsigned_word(_dummy_register, little_endian=True)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value",
    [
        [[0x01, 0x02], 0x0102],
        [[0x01, 0x08], 0x0108],
        [[0x01, 0x03], 0x0103],
        [[0x03, 0x04], 0x0304],
        [[0x07, 0x08], 0x0708],
    ],
)
def test_read_unsigned_word__big_endian(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_unsigned_word(_dummy_register, little_endian=False)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,expected_value",
    [
        [[0x01, 0x02], 0x0201],
        [[0x01, 0x08], 0x0801],
        [[0x01, 0x03], 0x0301],
        [[0x03, 0x04], 0x0403],
        [[0x07, 0x08], 0x0807],
    ],
)
def test_read_signed_word(setup_mocks, read_value, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_signed_word(_dummy_register, little_endian=True)
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,no_bytes_to_read,expected_value",
    [
        [[0x01], 1, 0x01],
        [[0x01, 0x08], 2, 0x0801],
        [[0x01, 0x02, 0x03], 3, 0x030201],
        [[0x01, 0x02, 0x03, 0x04], 4, 0x04030201],
        [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0807060504030201],
    ],
)
def test_read_n_unsigned_bytes(
    setup_mocks, read_value, no_bytes_to_read, expected_value
):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_n_unsigned_bytes(
        _dummy_register, no_bytes_to_read, little_endian=True
    )
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,no_bytes_to_read,expected_value",
    [
        [[0x01], 1, 0x01],
        [[0x01, 0x08], 2, 0x0801],
        [[0x01, 0x02, 0x03], 3, 0x030201],
        [[0x01, 0x02, 0x03, 0x04], 4, 0x04030201],
        [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0807060504030201],
    ],
)
def test_read_n_signed_bytes(setup_mocks, read_value, no_bytes_to_read, expected_value):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_n_signed_bytes(
        _dummy_register, no_bytes_to_read, little_endian=True
    )
    i2c_device.disconnect()

    assert expected_value == read_value


@pytest.mark.parametrize(
    "read_value,no_bytes_to_read,expected_value",
    [
        [[0x01], 1, 0x01],
        [[0x01, 0x08], 2, 0x0108],
        [[0x01, 0x02, 0x03], 3, 0x010203],
        [[0x01, 0x02, 0x03, 0x04], 4, 0x01020304],
        [[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], 8, 0x0102030405060708],
    ],
)
def test_read_n_unsigned_bytes__big_endian(
    setup_mocks, read_value, no_bytes_to_read, expected_value
):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_n_unsigned_bytes(
        _dummy_register, no_bytes_to_read, little_endian=False
    )
    i2c_device.disconnect()

    assert expected_value == read_value


def test_write_n_bytes_acquires_and_releases_lock(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    ptlock_mock = setup_mocks.get("ptlock_mock")

    test_data = [0x01, 0x02, 0x03]

    i2c_device.connect(read_test=False)
    i2c_device.write_n_bytes(_dummy_register, test_data)
    i2c_device.disconnect()

    ptlock_mock.__enter__.assert_called_once()
    ptlock_mock.__exit__.assert_called_once()


def test_no_transaction_leaves_lock_alone(setup_mocks):
    i2c_device = setup_mocks.get("i2c_device")
    ptlock_mock = setup_mocks.get("ptlock_mock")

    i2c_device.connect(read_test=False)
    i2c_device.disconnect()

    ptlock_mock.__enter__.assert_not_called()
    ptlock_mock.__exit__.assert_not_called()


@pytest.mark.parametrize(
    "read_value,no_bytes_to_read,expected_value", [[[0x01], 1, 0x01]]
)
def test_read_n_unsigned_bytes_acquires_and_releases_lock(
    setup_mocks, read_value, no_bytes_to_read, expected_value
):
    i2c_device = setup_mocks.get("i2c_device")
    mock_read_device = setup_mocks.get("mock_read_device")
    ptlock_mock = setup_mocks.get("ptlock_mock")

    mock_read_device.read.return_value = read_value
    i2c_device.connect(read_test=False)
    read_value = i2c_device.read_n_unsigned_bytes(
        _dummy_register, no_bytes_to_read, little_endian=True
    )
    i2c_device.disconnect()

    ptlock_mock.__enter__.assert_called_once()
    ptlock_mock.__exit__.assert_called_once()
