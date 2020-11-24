from enum import Enum


class DeviceName(Enum):
    pi_top_ceed = "pi-topCEED"
    pi_top_3 = "pi-top [3]"
    pi_top_4 = "pi-top [4]"


class FirmwareDeviceName(Enum):
    pt4_hub = "pi-top [4]"
    pt4_foundation_plate = "pi-top [4] Foundation Plate"
    pt4_expansion_plate = "pi-top [4] Expansion Plate"
