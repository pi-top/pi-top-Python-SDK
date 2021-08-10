from os import path
from getpass import getuser


def is_pi_top_os():
    return path.isfile("/etc/pt-issue")


def eula_agreed():
    return_value = False
    fts_file = "/etc/pi-top/.licenceAgreed"

    if path.isfile(fts_file):
        return_value = True

    return return_value


def is_pi_using_default_password():
    if getuser() == "root":
        with open("/etc/shadow") as shadow_file:
            for line in shadow_file:
                if "pi:" in line and "c4XjD2pO7T6KeaTJXLMFZ/" in line:
                    return True

        return False
    else:
        return None
