from pitopcommon.common_ids import DeviceID
from pitopcommon.ptdm import PTDMRequestClient, Message
from pitopcommon.firmware_device import FirmwareDevice
from pitopcommon.common_ids import FirmwareDeviceID

from subprocess import getstatusoutput


def __device_id():
    message = Message.from_parts(Message.REQ_GET_DEVICE_ID, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    parameters = response.parameters
    device_id = int(parameters[0])
    return device_id


def __device_name(device_id):
    device_lookup = {
        DeviceID.unknown.value: "Unknown",
        DeviceID.pi_top.value: "Original pi-top",
        DeviceID.pi_top_ceed.value: "pi-topCEED",
        DeviceID.pi_top_3.value: "pi-top [3]",
        DeviceID.pi_top_4.value: "pi-top [4]",
    }
    return device_lookup.get(device_id)


def device_type():
    return __device_name(__device_id())


def device_info():
    device_id = __device_id()
    return {
        "name": __device_name(device_id),
        "fw_version": device_firmware(device_id)
    }


def device_firmware(device_id):
    fw_device_lookup = {
        DeviceID.pi_top_4.value: FirmwareDeviceID.pt4_hub,
    }

    fw_device_id = fw_device_lookup.get(device_id)
    if fw_device_id is None:
        return ""

    device_info = FirmwareDevice.device_info.get(fw_device_id)
    device_address = device_info.get("i2c_addr")

    fw_version = None
    if getstatusoutput(f"pt-i2cdetect {device_address}"):
        try:
            fw_device = FirmwareDevice(fw_device_id)
            fw_version = fw_device.get_fw_version()
        except Exception:
            pass
    return fw_version
