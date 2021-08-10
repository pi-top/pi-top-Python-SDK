from enum import Enum


class DeviceName(Enum):
    pi_top_ceed = "pi-topCEED"
    pi_top_3 = "pi-top [3]"
    pi_top_4 = "pi-top [4]"


class PeripheralName(Enum):
    unknown = "Unknown"
    pi_top_pulse = "pi-topPULSE"
    pi_top_speaker_l = "pi-topSPEAKER (v1) - Left channel"
    pi_top_speaker_r = "pi-topSPEAKER (v1) - Right channel"
    pi_top_speaker_m = "pi-topSPEAKER (v1) - Mono"
    pi_top_speaker_v2 = "pi-topSPEAKER (v2)"
    pi_top_proto_plus = "pi-topPROTO+"


class FirmwareDeviceName(Enum):
    pt4_hub = "pi-top [4]"
    pt4_foundation_plate = "pi-top [4] Foundation Plate"
    pt4_expansion_plate = "pi-top [4] Expansion Plate"
