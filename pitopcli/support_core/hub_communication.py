from datetime import datetime
from math import ceil, floor

from pitop.common.i2c_device import I2CDevice

from ..formatter import StdoutFormat, StdoutTable


class HubCommunication:
    def __init__(self):
        self.device = None
        for addr in (0x11, 0x10):
            try:
                self.device = I2CDevice("/dev/i2c-1", addr)
                self.device.connect()
                break
            except Exception:
                pass

        if self.device is None:
            raise Exception(
                "This diagnostics tool only supports pi-top [3] and pi-top [4]"
            )

    def int_to_hex(self, value, no_of_bytes=8):
        return f"0x{hex(value)[2:].zfill(ceil(no_of_bytes / 2))}"

    def int_to_binary(self, value, no_of_bytes=1):
        return "{0:b}".format(value).zfill(8 * no_of_bytes)

    def int_to_mac_address(self, value):
        return ":".join(
            ["{}{}".format(a, b) for a, b in zip(*[iter("{:012x}".format(value))] * 2)]
        )

    def int_to_date(self, value):
        # Day + Month × 32 + (Year–1980) × 512
        year = floor(value / 512) + 1980
        month = floor((value - (512 * (year - 1980))) / 32)
        day = value - 512 * (year - 1980) - 32 * (month)

        # yyyy-mm-dd
        return str(year).zfill(4) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2)

    def int_to_date_unix(self, value):
        try:
            return datetime.utcfromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")
        except OverflowError:
            return "Returned value invalid"

    def print_hub_registers(self):
        try:
            t = StdoutTable()
            t.title_format = StdoutFormat.print_subsection

            data_arr = [
                (
                    "BRD_DETECT",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0x10))}",
                ),
                ("MODULE_DETECT", f"{self.device.read_unsigned_byte(0x11)}"),
                ("BATT_AND_DISP_I2C_MUX", f"{self.device.read_unsigned_byte(0x13)}"),
                (
                    "UI_OLED_CTRL",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0x14))}",
                ),
                (
                    "UI_BUTTON_CTRL",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0x15))}",
                ),
            ]
            t.add_section("Hardware Control and Status", data_arr)

            data_arr = [
                (
                    "UPTIME_STDBY",
                    f"{self.device.read_n_unsigned_bytes(0x20, number_of_bytes=4)} min",
                ),
                (
                    "UPTIME_RAILSON",
                    f"{self.device.read_n_unsigned_bytes(0x21, number_of_bytes=4)} min",
                ),
                (
                    "LIFETIME_STDBY",
                    f"{self.device.read_n_unsigned_bytes(0x22, number_of_bytes=4)} hour",
                ),
                (
                    "LIFETIME_RAILSON",
                    f"{self.device.read_n_unsigned_bytes(0x23, number_of_bytes=4)} hour",
                ),
                ("LIFETIME_ONOFFCYC", f"{self.device.read_unsigned_word(0x24)} cycle"),
            ]
            t.add_section("Diagnostics", data_arr)

            data_arr = [
                (
                    "KEYBOARD_MAC_ADDRESS",
                    f"{self.int_to_mac_address(self.device.read_n_unsigned_bytes(0x50, number_of_bytes=6))}",
                ),
                ("DOCK_FLAG", f"{self.device.read_unsigned_byte(0x51)}"),
                ("FW_VER", f"{self.device.read_unsigned_byte(0x52)}"),
                ("HW_VER", f"{self.device.read_unsigned_byte(0x53)}"),
                (
                    "BT_MASTER_MAC_ADDRESS",
                    f"{self.int_to_mac_address(self.device.read_n_unsigned_bytes(0x54, number_of_bytes=6))}",
                ),
                ("CHRG_THRSH_HUB", f"{self.device.read_unsigned_byte(0x55)}"),
                ("CHRG_THRSH_KBRD", f"{self.device.read_unsigned_byte(0x56)}"),
                ("CHARGED_FLAG", f"{self.device.read_unsigned_byte(0x57)}"),
                ("BATT_LEVEL", f"{self.device.read_unsigned_byte(0x58)}"),
                ("PAIRING_STATUS", f"{self.device.read_unsigned_byte(0x5A)}"),
            ]
            t.add_section("Keyboard Cotnrol and Status", data_arr)

            data_arr = [
                ("VOLT_BATT_IN", f"{self.device.read_unsigned_word(0x70)} mV"),
                ("VOLT_DC_IN", f"{self.device.read_unsigned_word(0x71)} mV"),
                ("VOLT_MPWR_IN", f"{self.device.read_unsigned_word(0x72)} mV"),
                ("VOLT_VSYS_PRST", f"{self.device.read_unsigned_word(0x73)} mV"),
                ("VOLT_5V_PRST", f"{self.device.read_unsigned_word(0x76)} mV"),
                ("VOLT_5V", f"{self.device.read_unsigned_word(0x77)} mV"),
                ("VOLT_5V_USB", f"{self.device.read_unsigned_word(0x78)} mV"),
                ("VOLT_3V3", f"{self.device.read_unsigned_word(0x7A)} mV"),
            ]
            t.add_section("Advanced Power and Debug", data_arr)

            data_arr = [
                (
                    "SHUTDOWN_CTRL",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0xA0))}",
                ),
                (
                    "BUTT_SHORT_HOLD_TURNON",
                    f"{float(self.device.read_unsigned_byte(0xA1)) / 10} sec",
                ),
                (
                    "BUTT_SHORT_HOLD_TURNOFF",
                    f"{float(self.device.read_unsigned_byte(0xA2)) / 10} sec sec",
                ),
                ("LAST_SHUTDOWN_REASON", f"{self.device.read_unsigned_byte(0xA4)}"),
                (
                    "BUTT_LONG_HOLD",
                    f"{float(self.device.read_unsigned_byte(0xA3)) / 10} sec sec",
                ),
                ("M1_TIMEOUT_MIN", f"{self.device.read_unsigned_word(0xAA)} sec"),
                ("M1_TIMEOUT_MAX", f"{self.device.read_unsigned_word(0xAB)} sec"),
                ("M2_TIMEOUT_MIN", f"{self.device.read_unsigned_word(0xAC)} sec"),
                ("M2_TIMEOUT_MAX", f"{self.device.read_unsigned_word(0xAD)} sec"),
                ("M3_TIMEOUT", f"{self.device.read_unsigned_word(0xAE)} sec"),
                (
                    "USB_5V_TIMEOUT",
                    f"{self.int_to_hex(self.device.read_unsigned_word(0xAF))}",
                ),
            ]
            t.add_section("Power Controls", data_arr)

            data_arr = [
                ("STORAGE_MODE", f"{self.device.read_unsigned_byte(0xB0)}"),
                (
                    "TEMPERATURE",
                    f"{float(self.device.read_unsigned_word(0xB1)) / 10} K",
                ),
                ("VOLTAGE", f"{self.device.read_unsigned_word(0xB2)} mV"),
                ("CURRENT", f"{self.device.read_unsigned_word(0xB3)} mA"),
                ("RSOC", f"{self.device.read_unsigned_byte(0xB4)} %"),
                ("TIME_TO_EMPTY", f"{self.device.read_unsigned_word(0xB5)} mins"),
                ("TIME_TO_FULL", f"{self.device.read_unsigned_word(0xB6)} mins"),
                ("VOLT_CELL1", f"{self.device.read_unsigned_word(0xB7)} mV"),
                ("VOLT_CELL2", f"{self.device.read_unsigned_word(0xB8)} mV"),
                ("VOLT_CELL3", f"{self.device.read_unsigned_word(0xB9)} mV"),
                ("VOLT_CELL4", f"{self.device.read_unsigned_word(0xBA)} mV"),
                ("PF_ERROR", f"{self.device.read_unsigned_byte(0xBB)}"),
                ("SERIAL_NUM", f"{self.device.read_unsigned_word(0xBC)}"),
                (
                    "MANUF_DATE",
                    f"{self.int_to_date(self.device.read_unsigned_word(0xBD))}",
                ),
                ("CHARGING_ERROR", f"{self.device.read_unsigned_byte(0xBF)}"),
            ]
            t.add_section("Battery Control and Status", data_arr)

            data_arr = [
                (
                    "AUD_CONFIG",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0xC0))}",
                ),
                (
                    "REAL_TIME_COUNTER",
                    f"{self.int_to_date_unix(self.device.read_n_unsigned_bytes(0xC1, number_of_bytes=4))}",
                ),
            ]
            t.add_section("Miscellaneous Features", data_arr)

            data_arr = [
                ("TEST_MODE", f"{self.device.read_unsigned_byte(0xD0)}"),
                (
                    "BACKLIGHT",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0xD1))}",
                ),
                (
                    "STATUS",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0xD2))}",
                ),
                (
                    "MUX_CONTROL",
                    f"{self.int_to_binary(self.device.read_unsigned_byte(0xD3))}",
                ),
            ]
            t.add_section("Display", data_arr)

            data_arr = [
                ("MCU_SOFT_VERS_MAJOR", f"{self.device.read_unsigned_byte(0xE0)}"),
                ("MCU_SOFT_VERS_MINOR", f"{self.device.read_unsigned_byte(0xE1)}"),
                ("SCH_REV_MAJOR", f"{self.device.read_unsigned_byte(0xE2)}"),
                ("SCH_REV_MINOR", f"{self.device.read_unsigned_byte(0xE3)}"),
                ("BRD_REV", f"{self.device.read_unsigned_byte(0xE4)}"),
                (
                    "PART_NAME",
                    f"{self.int_to_hex(self.device.read_unsigned_word(0xE5))}",
                ),
                (
                    "PART_NUMBER",
                    f"{self.int_to_hex(self.device.read_unsigned_word(0xE6))}",
                ),
                (
                    "SERIAL_ID",
                    f"{self.int_to_hex(self.device.read_n_unsigned_bytes(0xE7, 4))}",
                ),
                (
                    "DISPLAY_MCU_SOFT_VERS_MAJOR",
                    f"{self.device.read_unsigned_byte(0xE8)}",
                ),
                (
                    "DISPLAY_MCU_SOFT_VERS_MINOR",
                    f"{self.device.read_unsigned_byte(0xE9)}",
                ),
                ("DISPLAY_SCH_REV_MAJOR", f"{self.device.read_unsigned_byte(0xEA)}"),
                ("DISPLAY_SCH_REV_MINOR", f"{self.device.read_unsigned_byte(0xEB)}"),
                ("DISPLAY_BRD_REV", f"{self.device.read_unsigned_byte(0xEC)}"),
                (
                    "DISPLAY_PART_NAME",
                    f"{self.int_to_hex(self.device.read_unsigned_word(0xED))}",
                ),
                (
                    "DISPLAY_PART_NUMBER",
                    f"{self.int_to_hex(self.device.read_unsigned_word(0xEE))}",
                ),
                (
                    "DISPLAY_SERIAL_ID",
                    f"{self.int_to_hex(self.device.read_n_unsigned_bytes(0xEF, number_of_bytes=4))}",
                ),
            ]
            t.add_section("Device Information", data_arr)

            self.device.disconnect()
            t.print()
        except Exception as e:
            print(f"Error getting pi-topHUB hardware diagnostics: {e}")
