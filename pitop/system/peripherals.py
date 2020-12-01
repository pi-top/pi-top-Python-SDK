from pitopcommon.firmware_device import FirmwareDevice
from pitopcommon.ptdm import PTDMRequestClient, Message
from pitopcommon.command_runner import run_command

from subprocess import getstatusoutput


def legacy_pitop_peripherals():
    connected_peripherals = []

    # Get legacy peripheral devices from pt-device-manager
    for id in range(5):
        message = Message.from_parts(Message.REQ_GET_PERIPHERAL_ENABLED, [id])

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        if response._message_id != Message.RSP_GET_PERIPHERAL_ENABLED:
            raise Exception("Unable to determine if peripheral is enabled from pt-device-manager")

        if not response.validate_parameters([int]):
            raise Exception("Unable to validate if peripheral is enabled from pt-device-manager")

        p_names = ['pi-topPULSE',
                   'pi-topSPEAKER-v1-left',
                   'pi-topSPEAKER-v1-mono',
                   'pi-topSPEAKER-v1-right',
                   'pi-topSPEAKER-v2']

        p_enabled = (message.parameters()[0] == '1')

        if p_enabled:
            connected_peripherals.append(p_names[id])

    return connected_peripherals


def upgradable_pitop_peripherals():
    connected_peripherals = []

    for device_enum, device_info in FirmwareDevice.device_info.items():
        device_str = device_enum.name

        device_address = device_info.get("i2c_addr")

        if getstatusoutput(f"pt-i2cdetect {device_address}"):
            try:
                fw_device = FirmwareDevice(device_enum)
                human_readable_name = device_str.replace(
                    "_", " ").title().replace("Pt4", "pi-top [4]")

                peripheral = {
                    "name": human_readable_name,
                    "fw_version": fw_device.get_fw_version()
                }
                connected_peripherals.append(peripheral)
            except Exception:
                pass

    return connected_peripherals


def touchscreen_is_connected():
    resp = run_command("lsusb", timeout=3)
    for line in resp.split("\n"):
        fields = line.split(" ")
        if len(fields) < 6:
            continue
        device_id = fields[5]
        if device_id == "222a:0001":
            return True

    return False


def pitop_keyboard_is_connected():
    resp = run_command("lsusb", timeout=3)
    for line in resp.split("\n"):
        fields = line.split(" ")
        if len(fields) < 6:
            continue
        device_id = fields[5]
        if device_id == "1c4f:0063":
            return True

    return False
