from pitopcommon.common_ids import DeviceID
from pitopcommon.ptdm import PTDMRequestClient, Message


def device_type():
    message = Message.from_parts(Message.REQ_GET_DEVICE_ID, [])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    if response._message_id != Message.RSP_GET_DEVICE_ID:
        raise Exception("Unable to determine device type from pt-device-manager")

    if not response.validate_parameters([int]):
        raise Exception("Unable to validate device type from pt-device-manager")

    device_lookup = {
        DeviceID.unknown.value:  "Unknown",
        DeviceID.pi_top.value: "Original pi-top",
        DeviceID.pi_top_ceed.value: "pi-topCEED",
        DeviceID.pi_top_3.value: "pi-top [3]",
        DeviceID.pi_top_4.value: "pi-top [4]",
    }

    device_id = response.parameters()
    device_str = device_lookup.get(int(device_id[0]))

    return device_str
