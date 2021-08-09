from dataclasses import dataclass, asdict
from os import path
from getpass import getuser


ptissue_path = "/boot/pt-issue.txt"
legacy_ptissue_path = "/etc/pt-issue"


@dataclass
class PitopOsBuildInfoV1:
    schema_version: str
    build_type: str
    date: str
    build_time_os_version: str
    build_run_number: str
    commit: str

    @classmethod
    def from_os_build_info(cls, build_info):
        DELIMITER: str = "_"
        LOOKUP = {
            "S": "schema_version",
            "B": "build_type",
            "D": "date",
            "P": "build_time_os_version",
            "R": "build_run_number",
            "#": "commit",
        }
        build_info_fields = build_info.split(DELIMITER)
        build_info_dict = {LOOKUP.get(field[0]): field[1:] for field in build_info_fields}
        return cls(**build_info_dict)

    @property
    def name(self):
        return f"S{self.schema_version}_B_{self.build_type}_D{self.date}_P{self.build_time_os_version}_#{self.commit}_R{self.build_run_number}"

    def as_dict(self):
        return asdict(self)


def is_pi_top_os():
    return path.isfile(ptissue_path)


def _parse_ptissue(ptissue_path):
    data = {}
    with open(ptissue_path, 'r') as reader:
        for line in reader.readlines():
            content = line.split(":")
            if len(content) == 2:
                data[content[0].strip()] = content[1].strip()
    return data


def get_pitopOS_info():
    if not path.isfile(ptissue_path):
        return

    try:
        build_info = _parse_ptissue(ptissue_path)
        return PitopOsBuildInfoV1.from_os_build_info(build_info.get("Build ID"))
    except Exception:
        raise Exception("Couldn't detect a valid build ID schema")


def get_legacy_pitopOS_info():
    if not path.isfile(legacy_ptissue_path):
        return

    return _parse_ptissue(legacy_ptissue_path)


def is_pi_using_default_password():
    if getuser() == "root":
        with open("/etc/shadow") as shadow_file:
            for line in shadow_file:
                if "pi:" in line and "c4XjD2pO7T6KeaTJXLMFZ/" in line:
                    return True

        return False
    else:
        return None
