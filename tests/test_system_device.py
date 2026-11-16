from unittest.mock import patch

from pitop.common.common_ids import DeviceID


@patch("pitop.system.device.FirmwareDevice")
@patch("pitop.system.device.getstatusoutput")
def test_device_firmware_reads_hub_only_when_i2cping_finds_it(
    getstatusoutput_mock, firmware_device_mock
):
    from pitop.system.device import device_firmware

    firmware_device_mock.device_info.get.return_value = {"i2c_addr": 0x11}
    firmware_device_mock.return_value.get_fw_version.return_value = "5.6"

    getstatusoutput_mock.return_value = (1, "Error: no device found at 0x11")
    assert device_firmware(DeviceID.pi_top_4.value) is None
    firmware_device_mock.assert_not_called()

    getstatusoutput_mock.return_value = (0, "")
    assert device_firmware(DeviceID.pi_top_4.value) == "5.6"
    firmware_device_mock.assert_called_once()
