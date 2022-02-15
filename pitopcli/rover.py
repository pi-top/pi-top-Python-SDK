from os import path
from pathlib import Path
from subprocess import Popen, getstatusoutput
from sys import stderr

from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.common_names import DeviceName
from pitop.common.firmware_device import FirmwareDevice
from pitop.system import device_type

from .cli_base import CliBaseClass, PitopCliInvalidArgument


class RoverCLI(CliBaseClass):
    parser_help = "Run the Rover Remote Control webpage"
    cli_name = "rover"

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:
        if self.args.rover_subcommand == "start":
            return self.start_server()
        elif self.args.rover_subcommand == "stop":
            return self.stop_server()
        else:
            raise PitopCliInvalidArgument("oops")

    @classmethod
    def add_parser_arguments(cls, parser) -> None:
        subparser = parser.add_subparsers(
            title="Rover control utility",
            description=cls.parser_help,
            dest="rover_subcommand",
        )

        start_parser = subparser.add_parser(
            "start", help="Start the Rover control server"
        )
        start_parser.add_argument(
            "-p", "--port", type=int, help="Port to run the server on", default=8070
        )
        start_parser.add_argument(
            "-d",
            "--detach",
            action="store_true",
            help="Run the server as a background process",
        )

        subparser.add_parser("stop", help="Stop detached Rover control servers")

    def stop_server(self) -> int:
        file_dir = Path(__file__).parent.resolve()
        subprocess_file = path.abspath(path.join(file_dir, "rover_start_detach.py"))
        Popen(["pkill", "-f", f"python3 {subprocess_file}"])

    def start_server(self) -> int:
        def is_pitop_four():
            try:
                return device_type() == DeviceName.pi_top_4.value
            except Exception:
                return False

        def has_expansion_plate():
            # TODO replace with pitop.system.pitop_peripherals
            expansion_plate_info = FirmwareDevice.device_info.get(
                FirmwareDeviceID.pt4_expansion_plate
            )
            i2c_address = expansion_plate_info.get("i2c_addr")

            try:
                expansion_plate_connected = (
                    getstatusoutput(f"i2cping {i2c_address}")[0] == 0
                )
            except Exception:
                expansion_plate_connected = False
            return expansion_plate_connected

        if not is_pitop_four():
            print("This CLI only runs on a pi-top [4].", file=stderr)
            return 1

        if not has_expansion_plate():
            print(
                "No Expansion Plate detected - unable to start Rover.",
                file=stderr,
            )
            return 1

        if self.args.detach:
            file_dir = Path(__file__).parent.resolve()
            subprocess_file = path.abspath(path.join(file_dir, "rover_start_detach.py"))
            Popen(["python3", subprocess_file, str(self.args.port)])
        else:
            from pitop import Camera, DriveController, Pitop
            from pitop.common.formatting import is_url
            from pitop.common.sys_info import get_internal_ip
            from pitop.labs import RoverWebController

            rover = Pitop()
            rover.add_component(DriveController())
            rover.add_component(Camera())

            rover_controller = RoverWebController(
                port=self.args.port,
                get_frame=rover.camera.get_frame,
                drive=rover.drive,
            )

            for interface in ("wlan0", "ptusb0", "lo", "en0"):
                ip_address = get_internal_ip(interface)
                if is_url("http://" + ip_address):
                    break

            text = f"Rover Remote Control:\n{ip_address}:{self.args.port}"
            rover.miniscreen.display_text(text, font_size=12)

            rover_controller.serve_forever()
