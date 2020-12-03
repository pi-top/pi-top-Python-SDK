from pitopcommon.firmware_device import FirmwareDevice
from pitopcommon.ptdm import PTDMRequestClient, Message
from pitopcommon.command_runner import run_command

from subprocess import getstatusoutput


def legacy_pitop_peripherals():
    peripherals = []

    # Get legacy peripheral devices from pt-device-manager
    for id in range(5):
        message = Message.from_parts(Message.REQ_GET_PERIPHERAL_ENABLED, [id])

        with PTDMRequestClient() as request_client:
            request_client.send_message(message)

        p_names = ['pi-topPULSE',
                   'pi-topSPEAKER-v1-left',
                   'pi-topSPEAKER-v1-mono',
                   'pi-topSPEAKER-v1-right',
                   'pi-topSPEAKER-v2']

        p_enabled = (message.parameters()[0] == '1')

        peripherals.append({
            "name": p_names[id],
            "connected": p_enabled})

    return peripherals


def upgradable_pitop_peripherals():
    peripherals = []

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
                    "fw_version": fw_device.get_fw_version(),
                    "connected": True
                }
                peripherals.append(peripheral)
            except Exception:
                pass

    return peripherals


def usb_pitop_peripherals():
    return [{'name': 'pi-top Touchscreen', 'connected': touchscreen_is_connected()},
            {'name': 'pi-top Keyboard', 'connected': pitop_keyboard_is_connected()}]


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


def pitop_peripherals():
    return upgradable_pitop_peripherals() + usb_pitop_peripherals() + legacy_pitop_peripherals()
