import subprocess
import netifaces
from os import uname
from os import path
from fractions import Fraction
from isc_dhcp_leases import IscDhcpLeases

from pitop.common.command_runner import run_command


_, _, _, _, machine = uname()


def is_pi():
    return machine in ("armv7l", "aarch64")


def get_debian_version():
    version = None
    with open("/etc/os-release", "r") as f:
        for line in f:
            if "VERSION_ID=" in line:
                quote_wrapped_version = line.split("=")[1]
                version_str = quote_wrapped_version.replace(
                    '"', "").replace("\n", "")
                try:
                    version = int(version_str)
                except ValueError:
                    version = None
                break

    try:
        return int(version)
    except ValueError:
        return None


def get_network_strength(iface):
    strength = -1
    try:
        response_str = str(subprocess.check_output(
            ["iwconfig", iface]).decode("utf-8"))
        response_lines = response_str.splitlines()
        for line in response_lines:
            if "Link Quality" in line:
                strength_str = line.lstrip(" ").lstrip(
                    "Link Quality=").split(" ")[0]
                strength = int(Fraction(strength_str) * 100)
                break
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return str(strength) + "%"


def get_wifi_network_ssid():
    try:
        network_id = str(
            subprocess.check_output(["iwgetid", "-r"]).decode("utf-8")
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        network_id = "Error"

    return network_id


def get_internal_ip(iface="wlan0"):
    if iface not in netifaces.interfaces():
        return iface + " Not Found"

    try:
        addrs = netifaces.ifaddresses(iface)
    except Exception:
        return "Addresses Not Found"

    try:
        inet_addrs = addrs[netifaces.AF_INET][0]
    except Exception:
        return "Internet Addresses Not Found"

    try:
        internal_ip = inet_addrs['addr']
    except Exception:
        return "IP Not Found"

    return internal_ip


def start_systemd_service(service_name: str):
    try:
        run_command(f"systemctl start {service_name}", timeout=20, check=True, log_errors=False)
    except Exception:
        pass


def stop_systemd_service(service_name: str):
    try:
        run_command(f"systemctl stop {service_name}", timeout=20, check=False, log_errors=False)
    except Exception:
        pass


def get_systemd_active_state(service_name: str):
    try:
        state = run_command(f"systemctl is-active {service_name}", timeout=10, log_errors=False)
        state = str(state.strip())
    except Exception:
        state = "Unknown Error"
    finally:
        return state


def get_systemd_enabled_state(service_to_check: str):
    try:
        state = str(
            subprocess.check_output(
                ["systemctl", "is-enabled", service_to_check]
            ).decode("utf-8")
        )
    except subprocess.CalledProcessError as response:
        state = str(response.output.decode("utf-8"))
    except Exception:
        state = "Unknown Error"
    finally:
        return state.strip().capitalize()


def get_ssh_enabled_state():
    ssh_enabled_state = get_systemd_enabled_state("ssh")
    return ssh_enabled_state


def get_vnc_enabled_state():
    vnc_enabled_state = get_systemd_enabled_state(
        "vncserver-x11-serviced.service")
    return vnc_enabled_state


def get_pt_further_link_enabled_state():
    vnc_enabled_state = get_systemd_enabled_state(
        "pt-further-link.service")
    return vnc_enabled_state


def get_ap_mode_status():
    key_lookup = {
        "State": "state",
        "Access Point Network SSID": "ssid",
        "Access Point Wi-Fi Password": "passphrase",
        "Access Point IP Address": "ip_address",
    }

    data = {}
    try:
        ap_mode_status = run_command("/usr/bin/wifi-ap-sta status", timeout=10)
        for str in ap_mode_status.strip().split("\n"):
            k, v = str.split(":")
            key = key_lookup.get(k.strip())
            if key:
                data[key] = v.strip()
    except Exception:
        pass
    return data


def interface_is_up(interface_name):
    operstate_file = "/sys/class/net/" + interface_name + "/operstate"
    if not path.exists(operstate_file):
        return False

    contents = ""
    with open(operstate_file, "r") as file:
        contents = file.read()

    return "up" in contents


def get_address_for_ptusb_connected_device():
    def command_succeeds(cmd, timeout):
        try:
            run_command(cmd, timeout=timeout, check=True, log_errors=False)
            return True
        except Exception:
            return False

    if interface_is_up("ptusb0"):
        current_leases = IscDhcpLeases('/var/lib/dhcp/dhcpd.leases').get_current().values()
        current_leases = list(current_leases)
        current_leases.reverse()

        for lease in current_leases:
            # Windows machines won't respond to ping requests by default. Using arping
            # helps us on that case, but since it takes ~1.5s, it's used as a fallback
            if (command_succeeds(f"ping -c1 {lease.ip}", 0.1) or
                    command_succeeds(f"arping -c1 {lease.ip}", 2)):
                return lease.ip
    return ""
