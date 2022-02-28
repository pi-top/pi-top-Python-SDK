from sys import modules
from unittest import TestCase, skip
from unittest.mock import Mock

from parameterized import parameterized

# import after applying mocks
from pitop.common.common_ids import FirmwareDeviceID  # noqa: E402
from pitop.common.firmware_device import FirmwareDevice  # noqa: E402
from pitop.common.firmware_device import PTInvalidFirmwareDeviceException  # noqa: E402

mock_io = Mock()  # modules["io"] = Mock()
mock_lock = Mock()  # modules["pitop.common.lock"] = Mock()
mock_fcntl = Mock()  # modules["fcntl"] = Mock()
mock_time = Mock()  # modules["time"] = Mock()


@skip
class FirmwareDeviceTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        del modules["io"]
        del modules["pitop.common.lock"]
        del modules["fcntl"]
        del modules["time"]

    def tearDown(self):
        mock_io.reset_mock()
        mock_lock.reset_mock()
        mock_fcntl.reset_mock()
        mock_time.reset_mock()

    def __get_mocked_firmware_device(self, part_name=None):
        cls = FirmwareDevice
        if part_name:
            cls.get_part_name = Mock(return_value=part_name)
        return cls

    @parameterized.expand(
        [
            [FirmwareDeviceID.pt4_foundation_plate, 0x1111],
            [FirmwareDeviceID.pt4_expansion_plate, 0x2222],
        ]
    )
    def test_constructor_same_device_name(self, dev_id, part_name):
        """Tests instantiation when the device responds with the correct part
        name."""
        cls = self.__get_mocked_firmware_device(part_name)
        cls(dev_id)

    @parameterized.expand(
        [
            [FirmwareDeviceID.pt4_foundation_plate, 0x2222],
            [FirmwareDeviceID.pt4_expansion_plate, 0x1111],
        ]
    )
    def test_constructor_different_device_name(self, dev_id, part_name):
        """Tests constructor failure  when the device responds with the
        incorrect part name."""
        cls = self.__get_mocked_firmware_device(part_name)

        with self.assertRaises(PTInvalidFirmwareDeviceException):
            cls(dev_id)

    def test_constructor_invalid_id(self):
        """Tests constructor using invalid device id."""
        invalid_ids = [5, 6, 7, 8, 9, 0.5, -1, "asd"]

        for id in invalid_ids:
            with self.assertRaises(AttributeError):
                FirmwareDevice(id)

    def test_valid_ids(self):
        """Tests valid_device_ids() method to correspond with the devices ids
        from FirmwareDeviceID enum."""
        valid_ids = [
            FirmwareDeviceID.pt4_hub,
            FirmwareDeviceID.pt4_foundation_plate,
            FirmwareDeviceID.pt4_expansion_plate,
        ]

        self.assertEqual(set(valid_ids), set(FirmwareDevice.valid_device_ids()))
