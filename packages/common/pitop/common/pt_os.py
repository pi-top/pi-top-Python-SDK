import logging
from dataclasses import dataclass
from getpass import getuser
from os import path

import psutil


def get_boot_partition_path():
    try:
        for partition in psutil.disk_partitions():
            if (
                partition.mountpoint.startswith("/boot")
                and ".recovery" not in partition.mountpoint
            ):
                return partition.mountpoint
    except Exception as e:
        logging.error(f"Couldn't find boot partition: {e}")
    return ""


ptissue_path = f"{get_boot_partition_path()}/pt-issue.txt"
legacy_ptissue_path = "/etc/pt-issue"


@dataclass
class PitopOsBuildInfo:
    build_date: str = ""
    build_run_number: str = ""
    build_commit: str = ""
    # latest fields
    schema_version: str = ""
    build_type: str = ""
    build_os_version: str = ""
    # legacy fields
    build_name: str = ""
    build_repo: str = ""
    final_repo: str = ""


def is_pi_top_os():
    return path.isfile(ptissue_path) or path.isfile(legacy_ptissue_path)


def get_pitopOS_info():
    def file_to_dict(path_to_file):
        data = {}
        with open(path_to_file, "r") as reader:
            for line in reader.readlines():
                content = line.split(":")
                if len(content) == 2:
                    data[content[0].strip()] = content[1].strip()
        return data

    def parse_ptissue(build_info_path):
        DELIMITER: str = "_"
        LOOKUP = {
            "S": "schema_version",
            "B": "build_type",
            "D": "build_date",
            "P": "build_os_version",
            "R": "build_run_number",
            "#": "build_commit",
        }
        build_info_file_dict = file_to_dict(build_info_path)
        build_id = build_info_file_dict.get("Build ID")
        build_info_fields = build_id.split(DELIMITER)
        return {
            LOOKUP.get(field[0].replace(":", "")): field[1:]
            for field in build_info_fields
        }

    def parse_legacy_ptissue(build_info_path):
        LOOKUP = {
            "Build Name": "build_name",
            "Build Date": "build_date",
            "Build Number": "build_run_number",
            "Build Pipeline Commit Hash": "build_commit",
            "Build Apt Repo": "build_repo",
            "Final Apt Repo": "final_repo",
        }
        build_info_file_dict = file_to_dict(build_info_path)
        return {
            LOOKUP.get(field): value for field, value in build_info_file_dict.items()
        }

    if path.isfile(ptissue_path):
        build_info_dict = parse_ptissue(ptissue_path)
    elif path.isfile(legacy_ptissue_path):
        build_info_dict = parse_legacy_ptissue(legacy_ptissue_path)
    else:
        return None

    try:
        return PitopOsBuildInfo(**build_info_dict)
    except Exception:
        pass


def is_pi_using_default_password():
    if getuser() == "root":
        with open("/etc/shadow") as shadow_file:
            for line in shadow_file:
                if "pi:" in line and "SomeSalt" in line:
                    return True

        return False
    else:
        return None
