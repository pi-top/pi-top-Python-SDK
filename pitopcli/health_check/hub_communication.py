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

            print(f" └ BRD_DETECT: {self.int_to_binary(BRD_DETECT)}")
            print(f" └ MODULE_DETECT: {MODULE_DETECT}")
            print(f" └ BATT_AND_DISP_I2C_MUX: {BATT_AND_DISP_I2C_MUX}")
            print(f" └ UI_OLED_CTRL: {self.int_to_binary(UI_OLED_CTRL)}")
            print(f" └ UI_BUTTON_CTRL: {self.int_to_binary(UI_BUTTON_CTRL)}")

            print("")
            StdoutFormat.print_subsection("Diagnostics")

            UPTIME_STDBY = self.device.read_n_unsigned_bytes(0x20, number_of_bytes=4)
            UPTIME_RAILSON = self.device.read_n_unsigned_bytes(0x21, number_of_bytes=4)
            LIFETIME_STDBY = self.device.read_n_unsigned_bytes(0x22, number_of_bytes=4)
            LIFETIME_RAILSON = self.device.read_n_unsigned_bytes(0x23, number_of_bytes=4)
            LIFETIME_ONOFFCYC = self.device.read_unsigned_word(0x24)

            print(f" └ UPTIME_STDBY: {UPTIME_STDBY} mins")
            print(f" └ UPTIME_RAILSON: {UPTIME_RAILSON} mins")
            print(f" └ LIFETIME_STDBY: {LIFETIME_STDBY} hours")
            print(f" └ LIFETIME_RAILSON: {LIFETIME_RAILSON} hours")
            print(f" └ LIFETIME_ONOFFCYC: {LIFETIME_ONOFFCYC} cycles")

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

            print(f" └ KEYBOARD_MAC_ADDRESS: {self.int_to_mac_address(KEYBOARD_MAC_ADDRESS)}")
            print(f" └ DOCK_FLAG: {DOCK_FLAG}")
            print(f" └ FW_VER: {FW_VER}")
            print(f" └ HW_VER: {HW_VER}")
            print(f" └ BT_MASTER_MAC_ADDRESS: {self.int_to_mac_address(BT_MASTER_MAC_ADDRESS)}")
            print(f" └ CHRG_THRSH_HUB: {CHRG_THRSH_HUB} %")
            print(f" └ CHRG_THRSH_KBRD: {CHRG_THRSH_KBRD} %")
            print(f" └ CHARGED_FLAG: {CHARGED_FLAG}")
            print(f" └ BATT_LEVEL: {BATT_LEVEL} %")
            print(f" └ PAIRING_STATUS: {PAIRING_STATUS}")

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

            print(f" └ VOLT_BATT_IN: {VOLT_BATT_IN} mV")
            print(f" └ VOLT_DC_IN: {VOLT_DC_IN} mV")
            print(f" └ VOLT_MPWR_IN: {VOLT_MPWR_IN} mV")
            print(f" └ VOLT_VSYS_PRST: {VOLT_VSYS_PRST} mV")
            print(f" └ VOLT_5V_PRST: {VOLT_5V_PRST} mV")
            print(f" └ VOLT_5V: {VOLT_5V} mV")
            print(f" └ VOLT_5V_USB: {VOLT_5V_USB} mV")
            print(f" └ VOLT_3V3: {VOLT_3V3} mV")

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

            print(f" └ SHUTDOWN_CTRL: {self.int_to_binary(SHUTDOWN_CTRL)}")
            print(f" └ BUTT_SHORT_HOLD_TURNON: {float(BUTT_SHORT_HOLD_TURNON / 10)}  secs")
            print(f" └ BUTT_SHORT_HOLD_TURNOFF: {float(BUTT_SHORT_HOLD_TURNOFF / 10)}  secs")
            print(f" └ BUTT_LONG_HOLD: {float(BUTT_LONG_HOLD / 10)} secs")
            print(f" └ M1_TIMEOUT_MIN: {M1_TIMEOUT_MIN} secs")
            print(f" └ M1_TIMEOUT_MAX: {M1_TIMEOUT_MAX} secs")
            print(f" └ M2_TIMEOUT_MIN: {M2_TIMEOUT_MIN} secs")
            print(f" └ M2_TIMEOUT_MAX: {M2_TIMEOUT_MAX} secs")
            print(f" └ M3_TIMEOUT: {M3_TIMEOUT} secs")
            print(f" └ USB_5V_TIMEOUT: {self.int_to_hex(USB_5V_TIMEOUT)}")

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

            print(f" └ STORAGE_MODE: {STORAGE_MODE}")
            print(f" └ TEMPERATURE: {float(TEMPERATURE / 10)} K")
            print(f" └ VOLTAGE: {VOLTAGE} mV")
            print(f" └ CURRENT: {CURRENT} mA")
            print(f" └ RSOC: {RSOC} %")
            print(f" └ TIME_TO_EMPTY: {TIME_TO_EMPTY} mins")
            print(f" └ TIME_TO_FULL: {TIME_TO_FULL} mins")
            print(f" └ VOLT_CELL1: {VOLT_CELL1} mV")
            print(f" └ VOLT_CELL2: {VOLT_CELL2} mV")
            print(f" └ VOLT_CELL3: {VOLT_CELL3} mV")
            print(f" └ VOLT_CELL4: {VOLT_CELL4} mV")
            print(f" └ PF_ERROR: {PF_ERROR}")
            print(f" └ SERIAL_NUM: {SERIAL_NUM}")
            print(f" └ MANUF_DATE: {self.int_to_date(MANUF_DATE)}")
            print(f" └ CHARGING_ERROR: {CHARGING_ERROR}")

            print("")
            StdoutFormat.print_subsection("Miscellaneous Features")

            AUD_CONFIG = self.device.read_unsigned_byte(0xC0)
            REAL_TIME_COUNTER = self.device.read_n_unsigned_bytes(0xC1, number_of_bytes=4)

            print(f" └ AUD_CONFIG: {self.int_to_binary(AUD_CONFIG)}")
            print(f" └ REAL_TIME_COUNTER: {self.int_to_date_unix(REAL_TIME_COUNTER)}")

            print("")
            StdoutFormat.print_subsection("Display")

            TEST_MODE = self.device.read_unsigned_byte(0xD0)
            BACKLIGHT = self.device.read_unsigned_byte(0xD1)
            STATUS = self.device.read_unsigned_byte(0xD2)
            MUX_CONTROL = self.device.read_unsigned_byte(0xD3)

            print(f" └ TEST_MODE: {TEST_MODE}")
            print(f" └ BACKLIGHT: {self.int_to_binary(BACKLIGHT)}")
            print(f" └ STATUS: {self.int_to_binary(STATUS)}")
            print(f" └ MUX_CONTROL: {self.int_to_binary(MUX_CONTROL)}")

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

            print(f" └ MCU_SOFT_VERS_MAJOR: {MCU_SOFT_VERS_MAJOR}")
            print(f" └ MCU_SOFT_VERS_MINOR: {MCU_SOFT_VERS_MINOR}")
            print(f" └ SCH_REV_MAJOR: {SCH_REV_MAJOR}")
            print(f" └ SCH_REV_MINOR: {SCH_REV_MINOR}")
            print(f" └ BRD_REV: {BRD_REV}")
            print(f" └ PART_NAME: {self.int_to_hex(PART_NAME)}")
            print(f" └ PART_NUMBER: {self.int_to_hex(PART_NUMBER)}")
            print(f" └ SERIAL_ID: {self.int_to_hex(SERIAL_ID)}")
            print(f" └ DISPLAY_MCU_SOFT_VERS_MAJOR: {DISPLAY_MCU_SOFT_VERS_MAJOR}")
            print(f" └ DISPLAY_MCU_SOFT_VERS_MINOR: {DISPLAY_MCU_SOFT_VERS_MINOR}")
            print(f" └ DISPLAY_SCH_REV_MAJOR: {DISPLAY_SCH_REV_MAJOR}")
            print(f" └ DISPLAY_SCH_REV_MINOR: {DISPLAY_SCH_REV_MINOR}")
            print(f" └ DISPLAY_BRD_REV: {DISPLAY_BRD_REV}")
            print(f" └ DISPLAY_PART_NAME: {self.int_to_hex(DISPLAY_PART_NAME)}")
            print(f" └ DISPLAY_PART_NUMBER: {self.int_to_hex(DISPLAY_PART_NUMBER)}")
            print(f" └ DISPLAY_SERIAL_ID: {self.int_to_hex(DISPLAY_SERIAL_ID)}")

            self.device.disconnect()
        except Exception as e:
            print(f"Error getting pi-topHUB hardware diagnostics: {e}")
