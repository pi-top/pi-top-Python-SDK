from pitopcommon.command_runner import run_command
from pitopcommon.common_ids import FirmwareDeviceID, PeripheralID
from pitopcommon.common_names import PeripheralName
from pitopcommon.firmware_device import FirmwareDevice
from pitopcommon.ptdm import PTDMRequestClient, Message


def legacy_pitop_peripherals():
    """Returns a list with the status of legacy peripheral devices.

    Returns:
        list: list of dictionaries with the status of legacy peripherals
    """
    peripherals = []

    for peripheral_enum in PeripheralID:
        if peripheral_enum == PeripheralID.unknown:
            continue

        peripheral_id = peripheral_enum.value
        human_readable_name = PeripheralName[peripheral_enum.name].value

        message = Message.from_parts(Message.REQ_GET_PERIPHERAL_ENABLED, [peripheral_id])

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        p_enabled = (int(response.parameters[0]) == 1)
        peripherals.append({
            "name": human_readable_name,
            "connected": p_enabled})

    return peripherals


def __get_fw_device_status(device_enum):
    """ Returns a dictionary with the status of the given device enum """
    human_readable_name = device_enum.name.replace(
        "_", " ").title().replace("Pt4", "pi-top [4]")

    peripheral = {
        "name": human_readable_name,
        "fw_version": None,
        "connected": False
    }

    try:
        fw_device = FirmwareDevice(device_enum)
        peripheral["fw_version"] = fw_device.get_fw_version()
        peripheral["connected"] = True
    except Exception:
        pass

    return peripheral


def upgradable_pitop_peripherals():
    """Returns a list with the status of legacy peripheral devices.

    Returns:
        list: list of dictionaries with the status of upgradable peripherals
    """
    peripherals = []

    for device_enum, _ in FirmwareDevice.device_info.items():
        if device_enum is FirmwareDeviceID.pt4_hub:
            continue
        peripherals.append(__get_fw_device_status(device_enum))

    return peripherals


def connected_plate():
    """Detects which plate from the PMA is connected to the device.

    Returns:
        FirmwareDeviceID: device ID of the connected plate. None if not detected"""
    for plate_id in (FirmwareDeviceID.pt4_foundation_plate, FirmwareDeviceID.pt4_expansion_plate):
        status = __get_fw_device_status(plate_id)
        if status.get("connected") is True:
            return plate_id
    return None


def usb_pitop_peripherals():
    """Returns a list with the status of USB pi-top peripherals.

    Returns:
        list: list of dictionaries with the status of USB peripherals
    """
    return [{'name': 'pi-top Touchscreen', 'connected': touchscreen_is_connected()},
            {'name': 'pi-top Keyboard', 'connected': pitop_keyboard_is_connected()}]


def touchscreen_is_connected():
    """Checks if pi-top touchscreen is connected to the device"""
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
    """Checks if pi-top keyboard is connected to the device"""
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
    """Returns a list with the status of all pi-top peripherals

    Returns:
        list: list of dictionaries with the status of pi-top peripherals
    """
    return upgradable_pitop_peripherals() + usb_pitop_peripherals() + legacy_pitop_peripherals()
