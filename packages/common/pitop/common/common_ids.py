from enum import Enum


class BatteryChargingState(Enum):
    no_battery_detected = -1
    discharging = 0
    charging = 1
    full_battery = 2


class DeviceID(Enum):
    unknown = -1
    pi_top = 0
    pi_top_ceed = 1
    pi_top_3 = 2
    pi_top_4 = 3


class PeripheralID(Enum):
    unknown = -1
    pi_top_pulse = 0
    pi_top_speaker_l = 1
    pi_top_speaker_m = 2
    pi_top_speaker_r = 3
    pi_top_speaker_v2 = 4
    pi_top_proto_plus = 5


class PeripheralType(Enum):
    unknown = -1
    hat = 0
    addon = 1


class FirmwareDeviceID(Enum):
    unknown = -1
    pt4_hub = 0
    pt4_foundation_plate = 1
    pt4_expansion_plate = 2


class Peripheral:
    id = PeripheralID.unknown
    compatible_ids = list()
    name = ""
    type = PeripheralType.unknown
    addr = -1

    def __init__(self, name="", id=-1, addr=-1):
        if name == "pi-topPULSE" or id == PeripheralID.pi_top_pulse or addr == 0x24:
            self.config_pulse()
        elif (
            name == "pi-topSPEAKER-v1-Left"
            or id == PeripheralID.pi_top_speaker_l
            or addr == 0x71
        ):
            self.config_speaker_l()
        elif (
            name == "pi-topSPEAKER-v1-Mono"
            or id == PeripheralID.pi_top_speaker_m
            or addr == 0x73
        ):
            self.config_speaker_m()
        elif (
            name == "pi-topSPEAKER-v1-Right"
            or id == PeripheralID.pi_top_speaker_r
            or addr == 0x72
        ):
            self.config_speaker_r()
        elif (
            name == "pi-topSPEAKER-v2"
            or id == PeripheralID.pi_top_speaker_v2
            or addr == 0x43
        ):
            self.config_speaker_v2()
        elif (
            name == "pi-topPROTO+"
            or id == PeripheralID.pi_top_proto_plus
            or addr == 0x2A
        ):
            self.config_proto_plus()

    def config_pulse(self):
        self.id = PeripheralID.pi_top_pulse
        self.compatible_ids = [PeripheralID.pi_top_proto_plus]
        self.name = "pi-topPULSE"
        self.type = PeripheralType.hat
        self.addr = 0x24

    def config_speaker_l(self):
        self.id = PeripheralID.pi_top_speaker_l
        self.compatible_ids = [
            PeripheralID.pi_top_speaker_r,
            PeripheralID.pi_top_speaker_m,
        ]
        self.name = "pi-topSPEAKER-v1-Left"
        self.type = PeripheralType.addon
        self.addr = 0x71

    def config_speaker_m(self):
        self.id = PeripheralID.pi_top_speaker_m
        self.compatible_ids = [
            PeripheralID.pi_top_speaker_l,
            PeripheralID.pi_top_speaker_r,
        ]
        self.name = "pi-topSPEAKER-v1-Mono"
        self.type = PeripheralType.addon
        self.addr = 0x73

    def config_speaker_r(self):
        self.id = PeripheralID.pi_top_speaker_r
        self.compatible_ids = [
            PeripheralID.pi_top_speaker_l,
            PeripheralID.pi_top_speaker_m,
        ]
        self.name = "pi-topSPEAKER-v1-Right"
        self.type = PeripheralType.addon
        self.addr = 0x72

    def config_speaker_v2(self):
        self.id = PeripheralID.pi_top_speaker_v2
        self.compatible_ids = [PeripheralID.pi_top_proto_plus]
        self.name = "pi-topSPEAKER-v2"
        self.type = PeripheralType.addon
        self.addr = 0x43

    def config_proto_plus(self):
        self.id = PeripheralID.pi_top_proto_plus
        self.compatible_ids = [
            PeripheralID.pi_top_pulse,
            PeripheralID.pi_top_speaker_v2,
        ]
        self.name = "pi-topPROTO+"
        self.type = PeripheralType.addon
        self.addr = 0x2A
