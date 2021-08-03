from datetime import datetime
from math import ceil

from pitop.common.common_ids import FirmwareDeviceID
from pitop.common.i2c_device import I2CDevice


class PTInvalidFirmwareDeviceException(Exception):
    pass


class DeviceInfo:
    FW__UPGRADE_START = 0x01
    FW__UPGRADE_PACKET = 0x02
    FW__CHECK_FW_OKAY = 0x03
    # FW__GET_FW_VERSION = 0x04
    SYSTEM_REBOOT = 0x05
    FW_UPDATE_SCHEMA_VER = 0x06

    ID__MCU_SOFT_VERS_MAJOR = 0xE0
    ID__MCU_SOFT_VERS_MINOR = 0xE1
    ID__SCH_REV_MAJOR = 0xE2
    ID__SCH_REV_MINOR = 0xE3
    ID__BRD_REV = 0xE4
    ID__PART_NAME = 0xE5
    ID__PART_NUMBER = 0xE6
    ID__IS_RELEASE_BUILD = 0xE8
    ID__GIT_COMMIT_HASH = 0xE9
    ID__CI_BUILD_NO = 0xEA
    ID__BUILD_UNIX_TIMESTAMP = 0xEB


def int_to_hex(value, no_of_bytes=8):
    return hex(value)[2:].zfill(ceil(no_of_bytes / 2))


def int_to_date_unix(value):
    try:
        return datetime.utcfromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")
    except OverflowError:
        return "Returned value invalid"


class FirmwareDevice(object):
    device_info = {
        FirmwareDeviceID.pt4_hub: {"part_name": 0x0607, "i2c_addr": 0x11},
        FirmwareDeviceID.pt4_foundation_plate: {"part_name": 0x1111, "i2c_addr": 0x04},
        FirmwareDeviceID.pt4_expansion_plate: {"part_name": 0x2222, "i2c_addr": 0x04},
    }

    def __init__(
        self, id: FirmwareDeviceID, send_packet_interval: float = None
    ) -> None:
        if id not in self.device_info.keys():
            raise AttributeError("Invalid device Id")

        self.str_name = id.name
        self.addr = self.device_info[id]["i2c_addr"]
        self.part_name = self.device_info[id]["part_name"]
        self._i2c_device = I2CDevice("/dev/i2c-1", self.addr)

        if send_packet_interval:
            self._i2c_device.set_delays(send_packet_interval, send_packet_interval)

        try:
            self._i2c_device.connect()
        except Exception:
            raise ConnectionError("Device is not plugged. Skipping.")

        if self.part_name != self.get_part_name():
            raise PTInvalidFirmwareDeviceException(
                "Part name provided does not match. {} != {}".format(
                    hex(self.part_name), hex(self.get_part_name())
                )
            )

    @classmethod
    def valid_device_ids(self) -> list:
        return list(self.device_info.keys())

    def get_part_name(self) -> int:
        return self._i2c_device.read_unsigned_word(DeviceInfo.ID__PART_NAME)

    def get_sch_hardware_version_major(self) -> int:
        return self._i2c_device.read_unsigned_byte(DeviceInfo.ID__SCH_REV_MAJOR)

    def get_fw_version(self) -> str:
        major_ver = self.get_fw_version_major()
        minor_ver = self.get_fw_version_minor()
        return str(major_ver) + "." + str(minor_ver)

    def get_fw_version_major(self) -> int:
        return self._i2c_device.read_unsigned_byte(DeviceInfo.ID__MCU_SOFT_VERS_MAJOR)

    def get_fw_version_minor(self) -> int:
        return self._i2c_device.read_unsigned_byte(DeviceInfo.ID__MCU_SOFT_VERS_MINOR)

    def get_fw_version_update_schema(self) -> int:
        resp = self._i2c_device.read_n_unsigned_bytes(
            DeviceInfo.FW_UPDATE_SCHEMA_VER, 3
        )
        # First 2 bytes for verification: 0x55, 0xAA
        # Range is 55AA00 - 55AAFF
        if resp > 0x55AA00 and resp <= 0x55AAFF:
            return resp - 0x55AA00
        else:
            return 0

    def has_extended_build_info(self) -> bool:
        return self.get_raw_build_timestamp() != 0

    def get_is_release_build(self) -> bool:
        if self.has_extended_build_info():
            return None
        else:
            result = self._i2c_device.read_unsigned_byte(
                DeviceInfo.ID__IS_RELEASE_BUILD
            )
            return result == 1

    def get_git_commit_hash(self) -> int:
        if self.has_extended_build_info():
            return None
        else:
            return int_to_hex(
                self._i2c_device.read_n_unsigned_bytes(
                    DeviceInfo.ID__GIT_COMMIT_HASH, 4
                )
            )

    def get_ci_build_no(self) -> int:
        if self.has_extended_build_info():
            return None
        else:
            return self._i2c_device.read_unsigned_word(DeviceInfo.ID__CI_BUILD_NO)

    def get_raw_build_timestamp(self) -> str:
        return self._i2c_device.read_n_unsigned_bytes(
            DeviceInfo.ID__BUILD_UNIX_TIMESTAMP, 4
        )

    def get_build_timestamp(self) -> str:
        if self.has_extended_build_info():
            return None
        else:
            return int_to_date_unix(
                self._i2c_device.read_n_unsigned_bytes(
                    DeviceInfo.ID__BUILD_UNIX_TIMESTAMP, 4
                )
            )

    def send_packet(self, hardware_reg, packet) -> None:
        self._i2c_device.write_n_bytes(hardware_reg, packet)

    def get_check_fw_okay(self) -> int:
        return self._i2c_device.read_n_unsigned_bytes(DeviceInfo.FW__CHECK_FW_OKAY, 8)

    def reset(self):
        if self.get_fw_version_update_schema() >= 1:
            self._i2c_device.write_byte(DeviceInfo.SYSTEM_REBOOT, 1)

    @classmethod
    def str_name_to_device_id(cls, str_name: str) -> FirmwareDeviceID:
        devices = cls.valid_device_ids()
        if str_name not in [d.name for d in devices]:
            raise AttributeError("Invalid device name")
        return FirmwareDeviceID[str_name]
