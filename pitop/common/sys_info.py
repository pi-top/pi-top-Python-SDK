from fractions import Fraction
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from os import path, uname
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, check_output
from typing import Dict, Union

import netifaces
from isc_dhcp_leases import IscDhcpLeases

from pitop.common.command_runner import run_command

_, _, _, _, machine = uname()


def is_pi() -> bool:
    return machine in ("armv7l", "aarch64")


def get_uname_release() -> str:
    return uname().release


def get_uname_version() -> str:
    return uname().version


def get_debian_version() -> str:
    debian_version_file = "/etc/debian_version"
    if not path.exists(debian_version_file):
        return None
    with open(debian_version_file, "r") as reader:
        content = reader.read()
    return content.strip()


def get_maj_debian_version() -> str:
    version = None
    with open("/etc/os-release", "r") as f:
        for line in f:
            if "VERSION_ID=" in line:
                quote_wrapped_version = line.split("=")[1]
                version_str = quote_wrapped_version.replace('"', "").replace("\n", "")
                try:
                    version = int(version_str)
                except ValueError:
                    version = None
                break

    try:
        return int(version)
    except ValueError:
        return None


def get_network_strength(iface) -> str:
    strength = -1
    try:
        response_str = str(check_output(["iwconfig", iface]).decode("utf-8"))
        response_lines = response_str.splitlines()
        for line in response_lines:
            if "Link Quality" in line:
                strength_str = line.lstrip(" ").lstrip("Link Quality=").split(" ")[0]
                strength = int(Fraction(strength_str) * 100)
                break
    except (FileNotFoundError, CalledProcessError):
        pass

    return str(strength) + "%"


def get_wifi_network_ssid() -> str:
    try:
        network_id = str(check_output(["iwgetid", "-r"]).decode("utf-8")).strip()
    except (FileNotFoundError, CalledProcessError):
        network_id = "Error"

    return network_id


def get_internal_ip(iface="wlan0") -> str:
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
        internal_ip = inet_addrs["addr"]
    except Exception:
        return "IP Not Found"

    return internal_ip


def start_systemd_service(service_name: str) -> None:
    try:
        run_command(
            f"systemctl start {service_name}", timeout=20, check=True, log_errors=False
        )
    except Exception:
        pass


def stop_systemd_service(service_name: str) -> None:
    try:
        run_command(
            f"systemctl stop {service_name}", timeout=20, check=False, log_errors=False
        )
    except Exception:
        pass


def get_systemd_active_state(service_name: str) -> str:
    try:
        state = run_command(
            f"systemctl is-active {service_name}", timeout=10, log_errors=False
        )
        state = str(state.strip())
    except Exception:
        state = "Unknown Error"
    finally:
        return state


def get_systemd_enabled_state(service_to_check: str) -> str:
    try:
        state = str(
            check_output(["systemctl", "is-enabled", service_to_check]).decode("utf-8")
        )
    except CalledProcessError as response:
        state = str(response.output.decode("utf-8"))
    except Exception:
        state = "Unknown Error"
    finally:
        return state.strip().capitalize()


def get_ssh_enabled_state() -> bool:
    ssh_enabled_state = get_systemd_enabled_state("ssh")
    return ssh_enabled_state


def get_vnc_enabled_state() -> bool:
    vnc_enabled_state = get_systemd_enabled_state("vncserver-x11-serviced.service")
    return vnc_enabled_state


def get_pt_further_link_enabled_state() -> bool:
    vnc_enabled_state = get_systemd_enabled_state("further-link.service")
    return vnc_enabled_state


def get_ap_mode_status() -> Dict:
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


def interface_is_up(interface_name: str) -> bool:
    operstate_file = "/sys/class/net/" + interface_name + "/operstate"
    if not path.exists(operstate_file):
        return False

    contents = ""
    with open(operstate_file, "r") as file:
        contents = file.read()

    return "up" in contents


class InterfaceNetworkData:
    def __init__(self, interface):
        self.interface = interface
        self.ip = ip_address(get_internal_ip(self.interface))
        self.network = ip_network(f"{self.ip}/{self.netmask}", strict=False)

    @property
    def netmask(self):
        cmd = f"ifconfig {self.interface} " + "| awk '/netmask /{ print $4;}'"
        output = (
            Popen(cmd, shell=True, stdout=PIPE, stderr=DEVNULL).stdout.read().strip()
        )
        return output.decode("utf-8")


def get_address_for_connected_device(
    network: Union[None, IPv4Network, IPv6Network] = None
) -> str:
    def command_succeeds(cmd, timeout):
        try:
            run_command(cmd, timeout=timeout, check=True, log_errors=False)
            return True
        except Exception:
            return False

    current_leases = IscDhcpLeases("/var/lib/dhcp/dhcpd.leases").get_current().values()
    current_leases = list(current_leases)
    current_leases.reverse()

    for lease in current_leases:
        if network and ip_address(lease.ip) not in network:
            continue

        # Windows machines won't respond to ping requests by default. Using arping
        # helps us on that case, but since it takes ~1.5s, it's used as a fallback
        if command_succeeds(f"ping -c1 {lease.ip}", 0.1) or command_succeeds(
            f"arping -c1 {lease.ip}", 2
        ):
            return lease.ip

    return ""


def get_address_for_ptusb_connected_device() -> str:
    if interface_is_up("ptusb0"):
        return get_address_for_connected_device(
            network=InterfaceNetworkData("ptusb0").network
        )
    return ""


def get_address_for_ap_connected_device() -> str:
    if interface_is_up("wlan_ap0"):
        return get_address_for_connected_device(
            network=InterfaceNetworkData("wlan_ap0").network
        )
    return ""


def is_connected_to_internet() -> bool:
    try:
        run_command("ping -c1 8.8.8.8", timeout=2, check=True, log_errors=False)
        return True
    except Exception:
        return False
