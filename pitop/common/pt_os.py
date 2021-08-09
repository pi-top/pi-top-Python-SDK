from os import path
from getpass import getuser

ptissue_path = "/boot/pt-issue.txt"
legacy_ptissue_path = "/etc/pt-issue"


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

    return _parse_ptissue(ptissue_path)


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
