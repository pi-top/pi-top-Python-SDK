#! /usr/bin/python3

from pitop.system import device_type

from .cli_base import CliBaseClass, PitopCliInvalidArgument
from .imu_calibration import ImuCalibration

from pitopcommon.common_ids import FirmwareDeviceID
from pitopcommon.common_names import DeviceName
from pitopcommon.firmware_device import FirmwareDevice

from os import path
from subprocess import getstatusoutput
from sys import stderr


class ImuCLI(CliBaseClass):
    parser_help = 'Expansion Plate IMU utilities'
    cli_name = 'imu'

    def __init__(self, args) -> None:
        self.args = args

    def run(self) -> int:
        # Check if device is a pi-top[4]
        is_pi_four = device_type() == DeviceName.pi_top_4.value
        if not is_pi_four:
            print("This CLI only runs on a pi-top [4].", file=stderr)
            return 1

        # Check if Expansion Plate is connected
        expansion_plate_info = FirmwareDevice.device_info.get(FirmwareDeviceID.pt4_expansion_plate)
        i2c_address = expansion_plate_info.get('i2c_addr')
        try:
            expansion_plate_connected = getstatusoutput(f"pt-i2cdetect {i2c_address}")[0] == 0
        except Exception:
            expansion_plate_connected = False
        if not expansion_plate_connected:
            print("No Expansion Plate detected - unable to calibrate IMU.", file=stderr)
            return 1

        if self.args.imu_subcommand == "calibrate":
            if self.args.path and not path.isdir(self.args.path):
                print(f"{self.args.path} is not a valid directory")
                return 1

            imu_cal = ImuCalibration()
            imu_cal.calibrate_magnetometer()
            imu_cal.plot_graphs(self.args.path)
        else:
            raise PitopCliInvalidArgument("oops")
        return 0

    @classmethod
    def add_parser_arguments(cls, parser) -> None:

        subparser = parser.add_subparsers(title="IMU utility",
                                          description=cls.parser_help,
                                          dest="imu_subcommand")

        calibrate_parser = subparser.add_parser("calibrate", help="Calibrate the magnetometer")
        calibrate_parser.add_argument("-p", "--path",
                                      type=str,
                                      help="Directory for storing calibration graph data"
                                      )
