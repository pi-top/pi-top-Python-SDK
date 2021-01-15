#!/usr/bin/python3
from math import ceil
from math import floor
from datetime import datetime

from pitopcommon.i2c_device import I2CDevice

from ..formatter import StdoutFormat


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
            raise Exception("This diagnostics tool only supports pi-top [3] and pi-top [4]")

    def int_to_hex(self, value, no_of_bytes=8):
        return f"0x{hex(value)[2:].zfill(ceil(no_of_bytes / 2))}"

    def int_to_binary(self, value, no_of_bytes=1):
        return "{0:b}".format(value).zfill(8 * no_of_bytes)

    def int_to_mac_address(self, value):
        return ":".join(
            ["{}{}".format(a, b)
             for a, b in zip(*[iter("{:012x}".format(value))] * 2)]
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
            StdoutFormat.print_subsection("Hardware Control and Status")

            BRD_DETECT = self.device.read_unsigned_byte(0x10)
            MODULE_DETECT = self.device.read_unsigned_byte(0x11)
            BATT_AND_DISP_I2C_MUX = self.device.read_unsigned_byte(0x13)
            UI_OLED_CTRL = self.device.read_unsigned_byte(0x14)
            UI_BUTTON_CTRL = self.device.read_unsigned_byte(0x15)

            StdoutFormat.print_line(f"BRD_DETECT: {self.int_to_binary(BRD_DETECT)}")
            StdoutFormat.print_line(f"MODULE_DETECT: {MODULE_DETECT}")
            StdoutFormat.print_line(f"BATT_AND_DISP_I2C_MUX: {BATT_AND_DISP_I2C_MUX}")
            StdoutFormat.print_line(f"UI_OLED_CTRL: {self.int_to_binary(UI_OLED_CTRL)}")
            StdoutFormat.print_line(f"UI_BUTTON_CTRL: {self.int_to_binary(UI_BUTTON_CTRL)}")

            print("")
            StdoutFormat.print_subsection("Diagnostics")

            UPTIME_STDBY = self.device.read_n_unsigned_bytes(0x20, number_of_bytes=4)
            UPTIME_RAILSON = self.device.read_n_unsigned_bytes(0x21, number_of_bytes=4)
            LIFETIME_STDBY = self.device.read_n_unsigned_bytes(0x22, number_of_bytes=4)
            LIFETIME_RAILSON = self.device.read_n_unsigned_bytes(0x23, number_of_bytes=4)
            LIFETIME_ONOFFCYC = self.device.read_unsigned_word(0x24)

            StdoutFormat.print_line(f"UPTIME_STDBY: {UPTIME_STDBY} mins")
            StdoutFormat.print_line(f"UPTIME_RAILSON: {UPTIME_RAILSON} mins")
            StdoutFormat.print_line(f"LIFETIME_STDBY: {LIFETIME_STDBY} hours")
            StdoutFormat.print_line(f"LIFETIME_RAILSON: {LIFETIME_RAILSON} hours")
            StdoutFormat.print_line(f"LIFETIME_ONOFFCYC: {LIFETIME_ONOFFCYC} cycles")

            print("")
            StdoutFormat.print_subsection("Keyboard Control and Status")

            KEYBOARD_MAC_ADDRESS = self.device.read_n_unsigned_bytes(
                0x50, number_of_bytes=6)
            DOCK_FLAG = self.device.read_unsigned_byte(0x51)
            FW_VER = self.device.read_unsigned_byte(0x52)
            HW_VER = self.device.read_unsigned_byte(0x53)
            BT_MASTER_MAC_ADDRESS = self.device.read_n_unsigned_bytes(
                0x54, number_of_bytes=6)
            CHRG_THRSH_HUB = self.device.read_unsigned_byte(0x55)
            CHRG_THRSH_KBRD = self.device.read_unsigned_byte(0x56)
            CHARGED_FLAG = self.device.read_unsigned_byte(0x57)
            BATT_LEVEL = self.device.read_unsigned_byte(0x58)
            PAIRING_STATUS = self.device.read_unsigned_byte(0x5A)

            StdoutFormat.print_line(f"KEYBOARD_MAC_ADDRESS: {self.int_to_mac_address(KEYBOARD_MAC_ADDRESS)}")
            StdoutFormat.print_line(f"DOCK_FLAG: {DOCK_FLAG}")
            StdoutFormat.print_line(f"FW_VER: {FW_VER}")
            StdoutFormat.print_line(f"HW_VER: {HW_VER}")
            StdoutFormat.print_line(f"BT_MASTER_MAC_ADDRESS: {self.int_to_mac_address(BT_MASTER_MAC_ADDRESS)}")
            StdoutFormat.print_line(f"CHRG_THRSH_HUB: {CHRG_THRSH_HUB} %")
            StdoutFormat.print_line(f"CHRG_THRSH_KBRD: {CHRG_THRSH_KBRD} %")
            StdoutFormat.print_line(f"CHARGED_FLAG: {CHARGED_FLAG}")
            StdoutFormat.print_line(f"BATT_LEVEL: {BATT_LEVEL} %")
            StdoutFormat.print_line(f"PAIRING_STATUS: {PAIRING_STATUS}")

            print("")
            StdoutFormat.print_subsection("Advanced Power and Debug")

            VOLT_BATT_IN = self.device.read_unsigned_word(0x70)
            VOLT_DC_IN = self.device.read_unsigned_word(0x71)
            VOLT_MPWR_IN = self.device.read_unsigned_word(0x72)
            VOLT_VSYS_PRST = self.device.read_unsigned_word(0x73)
            VOLT_5V_PRST = self.device.read_unsigned_word(0x76)
            VOLT_5V = self.device.read_unsigned_word(0x77)
            VOLT_5V_USB = self.device.read_unsigned_word(0x78)
            VOLT_3V3 = self.device.read_unsigned_word(0x7A)

            StdoutFormat.print_line(f"VOLT_BATT_IN: {VOLT_BATT_IN} mV")
            StdoutFormat.print_line(f"VOLT_DC_IN: {VOLT_DC_IN} mV")
            StdoutFormat.print_line(f"VOLT_MPWR_IN: {VOLT_MPWR_IN} mV")
            StdoutFormat.print_line(f"VOLT_VSYS_PRST: {VOLT_VSYS_PRST} mV")
            StdoutFormat.print_line(f"VOLT_5V_PRST: {VOLT_5V_PRST} mV")
            StdoutFormat.print_line(f"VOLT_5V: {VOLT_5V} mV")
            StdoutFormat.print_line(f"VOLT_5V_USB: {VOLT_5V_USB} mV")
            StdoutFormat.print_line(f"VOLT_3V3: {VOLT_3V3} mV")

            print("")
            StdoutFormat.print_subsection("Power Controls")

            SHUTDOWN_CTRL = self.device.read_unsigned_byte(0xA0)
            BUTT_SHORT_HOLD_TURNON = self.device.read_unsigned_byte(0xA1)
            BUTT_SHORT_HOLD_TURNOFF = self.device.read_unsigned_byte(0xA2)
            BUTT_LONG_HOLD = self.device.read_unsigned_byte(0xA3)
            M1_TIMEOUT_MIN = self.device.read_unsigned_word(0xAA)
            M1_TIMEOUT_MAX = self.device.read_unsigned_word(0xAB)
            M2_TIMEOUT_MIN = self.device.read_unsigned_word(0xAC)
            M2_TIMEOUT_MAX = self.device.read_unsigned_word(0xAD)
            M3_TIMEOUT = self.device.read_unsigned_word(0xAE)
            USB_5V_TIMEOUT = self.device.read_unsigned_word(0xAF)

            StdoutFormat.print_line(f"SHUTDOWN_CTRL: {self.int_to_binary(SHUTDOWN_CTRL)}")
            StdoutFormat.print_line(f"BUTT_SHORT_HOLD_TURNON: {float(BUTT_SHORT_HOLD_TURNON / 10)}  secs")
            StdoutFormat.print_line(f"BUTT_SHORT_HOLD_TURNOFF: {float(BUTT_SHORT_HOLD_TURNOFF / 10)}  secs")
            StdoutFormat.print_line(f"BUTT_LONG_HOLD: {float(BUTT_LONG_HOLD / 10)} secs")
            StdoutFormat.print_line(f"M1_TIMEOUT_MIN: {M1_TIMEOUT_MIN} secs")
            StdoutFormat.print_line(f"M1_TIMEOUT_MAX: {M1_TIMEOUT_MAX} secs")
            StdoutFormat.print_line(f"M2_TIMEOUT_MIN: {M2_TIMEOUT_MIN} secs")
            StdoutFormat.print_line(f"M2_TIMEOUT_MAX: {M2_TIMEOUT_MAX} secs")
            StdoutFormat.print_line(f"M3_TIMEOUT: {M3_TIMEOUT} secs")
            StdoutFormat.print_line(f"USB_5V_TIMEOUT: {self.int_to_hex(USB_5V_TIMEOUT)}")

            print("")
            StdoutFormat.print_subsection("Battery Control and Status")

            STORAGE_MODE = self.device.read_unsigned_byte(0xB0)
            TEMPERATURE = self.device.read_unsigned_word(0xB1)
            VOLTAGE = self.device.read_unsigned_word(0xB2)
            CURRENT = self.device.read_unsigned_word(0xB3)
            RSOC = self.device.read_unsigned_byte(0xB4)
            TIME_TO_EMPTY = self.device.read_unsigned_word(0xB5)
            TIME_TO_FULL = self.device.read_unsigned_word(0xB6)
            VOLT_CELL1 = self.device.read_unsigned_word(0xB7)
            VOLT_CELL2 = self.device.read_unsigned_word(0xB8)
            VOLT_CELL3 = self.device.read_unsigned_word(0xB9)
            VOLT_CELL4 = self.device.read_unsigned_word(0xBA)
            PF_ERROR = self.device.read_unsigned_byte(0xBB)
            SERIAL_NUM = self.device.read_unsigned_word(0xBC)
            MANUF_DATE = self.device.read_unsigned_word(0xBD)
            CHARGING_ERROR = self.device.read_unsigned_byte(0xBF)

            StdoutFormat.print_line(f"STORAGE_MODE: {STORAGE_MODE}")
            StdoutFormat.print_line(f"TEMPERATURE: {float(TEMPERATURE / 10)} K")
            StdoutFormat.print_line(f"VOLTAGE: {VOLTAGE} mV")
            StdoutFormat.print_line(f"CURRENT: {CURRENT} mA")
            StdoutFormat.print_line(f"RSOC: {RSOC} %")
            StdoutFormat.print_line(f"TIME_TO_EMPTY: {TIME_TO_EMPTY} mins")
            StdoutFormat.print_line(f"TIME_TO_FULL: {TIME_TO_FULL} mins")
            StdoutFormat.print_line(f"VOLT_CELL1: {VOLT_CELL1} mV")
            StdoutFormat.print_line(f"VOLT_CELL2: {VOLT_CELL2} mV")
            StdoutFormat.print_line(f"VOLT_CELL3: {VOLT_CELL3} mV")
            StdoutFormat.print_line(f"VOLT_CELL4: {VOLT_CELL4} mV")
            StdoutFormat.print_line(f"PF_ERROR: {PF_ERROR}")
            StdoutFormat.print_line(f"SERIAL_NUM: {SERIAL_NUM}")
            StdoutFormat.print_line(f"MANUF_DATE: {self.int_to_date(MANUF_DATE)}")
            StdoutFormat.print_line(f"CHARGING_ERROR: {CHARGING_ERROR}")

            print("")
            StdoutFormat.print_subsection("Miscellaneous Features")

            AUD_CONFIG = self.device.read_unsigned_byte(0xC0)
            REAL_TIME_COUNTER = self.device.read_n_unsigned_bytes(0xC1, number_of_bytes=4)

            StdoutFormat.print_line(f"AUD_CONFIG: {self.int_to_binary(AUD_CONFIG)}")
            StdoutFormat.print_line(f"REAL_TIME_COUNTER: {self.int_to_date_unix(REAL_TIME_COUNTER)}")

            print("")
            StdoutFormat.print_subsection("Display")

            TEST_MODE = self.device.read_unsigned_byte(0xD0)
            BACKLIGHT = self.device.read_unsigned_byte(0xD1)
            STATUS = self.device.read_unsigned_byte(0xD2)
            MUX_CONTROL = self.device.read_unsigned_byte(0xD3)

            StdoutFormat.print_line(f"TEST_MODE: {TEST_MODE}")
            StdoutFormat.print_line(f"BACKLIGHT: {self.int_to_binary(BACKLIGHT)}")
            StdoutFormat.print_line(f"STATUS: {self.int_to_binary(STATUS)}")
            StdoutFormat.print_line(f"MUX_CONTROL: {self.int_to_binary(MUX_CONTROL)}")

            print("")
            StdoutFormat.print_subsection("Device Information")

            MCU_SOFT_VERS_MAJOR = self.device.read_unsigned_byte(0xE0)
            MCU_SOFT_VERS_MINOR = self.device.read_unsigned_byte(0xE1)
            SCH_REV_MAJOR = self.device.read_unsigned_byte(0xE2)
            SCH_REV_MINOR = self.device.read_unsigned_byte(0xE3)
            BRD_REV = self.device.read_unsigned_byte(0xE4)
            PART_NAME = self.device.read_unsigned_word(0xE5)
            PART_NUMBER = self.device.read_unsigned_word(0xE6)
            SERIAL_ID = self.device.read_n_unsigned_bytes(0xE7, 4)
            DISPLAY_MCU_SOFT_VERS_MAJOR = self.device.read_unsigned_byte(0xE8)
            DISPLAY_MCU_SOFT_VERS_MINOR = self.device.read_unsigned_byte(0xE9)
            DISPLAY_SCH_REV_MAJOR = self.device.read_unsigned_byte(0xEA)
            DISPLAY_SCH_REV_MINOR = self.device.read_unsigned_byte(0xEB)
            DISPLAY_BRD_REV = self.device.read_unsigned_byte(0xEC)
            DISPLAY_PART_NAME = self.device.read_unsigned_word(0xED)
            DISPLAY_PART_NUMBER = self.device.read_unsigned_word(0xEE)
            DISPLAY_SERIAL_ID = self.device.read_n_unsigned_bytes(0xEF, number_of_bytes=4)

            StdoutFormat.print_line(f"MCU_SOFT_VERS_MAJOR: {MCU_SOFT_VERS_MAJOR}")
            StdoutFormat.print_line(f"MCU_SOFT_VERS_MINOR: {MCU_SOFT_VERS_MINOR}")
            StdoutFormat.print_line(f"SCH_REV_MAJOR: {SCH_REV_MAJOR}")
            StdoutFormat.print_line(f"SCH_REV_MINOR: {SCH_REV_MINOR}")
            StdoutFormat.print_line(f"BRD_REV: {BRD_REV}")
            StdoutFormat.print_line(f"PART_NAME: {self.int_to_hex(PART_NAME)}")
            StdoutFormat.print_line(f"PART_NUMBER: {self.int_to_hex(PART_NUMBER)}")
            StdoutFormat.print_line(f"SERIAL_ID: {self.int_to_hex(SERIAL_ID)}")
            StdoutFormat.print_line(f"DISPLAY_MCU_SOFT_VERS_MAJOR: {DISPLAY_MCU_SOFT_VERS_MAJOR}")
            StdoutFormat.print_line(f"DISPLAY_MCU_SOFT_VERS_MINOR: {DISPLAY_MCU_SOFT_VERS_MINOR}")
            StdoutFormat.print_line(f"DISPLAY_SCH_REV_MAJOR: {DISPLAY_SCH_REV_MAJOR}")
            StdoutFormat.print_line(f"DISPLAY_SCH_REV_MINOR: {DISPLAY_SCH_REV_MINOR}")
            StdoutFormat.print_line(f"DISPLAY_BRD_REV: {DISPLAY_BRD_REV}")
            StdoutFormat.print_line(f"DISPLAY_PART_NAME: {self.int_to_hex(DISPLAY_PART_NAME)}")
            StdoutFormat.print_line(f"DISPLAY_PART_NUMBER: {self.int_to_hex(DISPLAY_PART_NUMBER)}")
            StdoutFormat.print_line(f"DISPLAY_SERIAL_ID: {self.int_to_hex(DISPLAY_SERIAL_ID)}")

            self.device.disconnect()
        except Exception as e:
            print(f"Error getting pi-topHUB hardware diagnostics: {e}")
