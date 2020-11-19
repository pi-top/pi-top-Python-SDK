#! /usr/bin/python3

from subprocess import getstatusoutput

from pitop.utils.firmware_device import FirmwareDevice
from pitop.utils.command_runner import run_command
from pitop.utils.ptdm_message import Message
from pitop.utils.common_ids import DeviceID

from pt_cli_base import CliBaseClass


class DeviceCLI(CliBaseClass):
    parser_help = 'Get information about device and attached pi-top hardware'
    cli_name = 'device'

    def __init__(self, pt_socket, args) -> None:
        self.args = args
        self.socket = pt_socket

    def run(self) -> None:
        # Get host device and legacy peripheral devices from pt-device-manager
        try:
            message = self.socket.send_request(Message.REQ_GET_DEVICE_ID)
            self.print_device_id(message)

            for id in range(5):
                message = self.socket.send_request(Message.REQ_GET_PERIPHERAL_ENABLED, [id])
                self.print_peripheral_enabled(message, id)
        except Exception as e:
            print(f"Unable to get information from pt-device-manager: {e}")

        # Get touchscreen/keyboard from USB devices
        touchscreen_connected = False
        keyboard_connected = False

        resp = run_command("lsusb", timeout=3)
        for line in resp.split("\n"):
            fields = line.split(" ")
            if len(fields) < 6:
                continue
            device_id = fields[5]
            if device_id == "222a:0001":
                touchscreen_connected = True
            elif device_id == "1c4f:0063":
                keyboard_connected = True

            if touchscreen_connected and keyboard_connected:
                break

        print(f"pi-top Touchscreen: {'' if touchscreen_connected else 'not '}connected")
        print(f"pi-top Keyboard: {'' if keyboard_connected else 'not '}connected")

        # Firmware-upgradable pi-top peripherals
        if "pi-top [4]" not in run_command("pt-host", timeout=3):
            return

        for device_enum, device_info in FirmwareDevice.device_info.items():
            device_str = device_enum.name

            device_address = device_info.get("i2c_addr")

            if getstatusoutput(f"pt-i2cdetect {device_address}"):
                try:
                    fw_device = FirmwareDevice(device_enum)
                    human_readable_name = device_str.replace(
                        "_", " ").title().replace("Pt4", "pi-top [4]")
                    print(
                        f"Upgradable device connected: {human_readable_name} (v{fw_device.get_fw_version()})")
                except:
                    pass

    def print_device_id(self, message) -> None:
        if message.message_id() == Message.RSP_GET_DEVICE_ID:
            if message.validate_parameters([int]):
                device_id = message.parameters()
                if int(device_id[0]) == DeviceID.pi_top.value:
                    print("Host device: original pi-top")
                elif int(device_id[0]) == DeviceID.pi_top_ceed.value:
                    print("Host device: pi-topCEED")
                elif int(device_id[0]) == DeviceID.pi_top_3.value:
                    print("Host device: pi-top [3]")
                elif int(device_id[0]) == DeviceID.pi_top_4.value:
                    print("Host device: pi-top [4]")
                else:
                    print("Host device: Unknown")
            else:
                print("Error: Unable to get valid device ID.")

    def print_peripheral_enabled(self, message, id) -> None:
        p_names = ['pi-topPULSE',
                   'pi-topSPEAKER-v1-left',
                   'pi-topSPEAKER-v1-mono',
                   'pi-topSPEAKER-v1-right',
                   'pi-topSPEAKER-v2']

        if message.message_id() == Message.RSP_GET_PERIPHERAL_ENABLED:
            if message.validate_parameters([int]):
                p_enabled = message.parameters()

                if p_enabled[0] == '1':
                    print(f"Connected device: {p_names[id]}")
            else:
                print("Unable to get valid peripheral enabled.")
   
    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        pass

if __name__ == "__main__":
    from deprecated_cli_runner import run
    run(DeviceCLI)
