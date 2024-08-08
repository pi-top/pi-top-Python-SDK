import logging
import re
from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from os import path, uname
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, check_output
from typing import Dict, Union

import netifaces
from isc_dhcp_leases import IscDhcpLeases

from pitop.common.command_runner import run_command

logger = logging.getLogger(__name__)


class NetworkInterface(Enum):
    eth0 = auto()
    wlan0 = auto()
    wlan_ap0 = auto()
    ptusb0 = auto()


def is_pi() -> bool:
    return uname().machine in ("armv7l", "aarch64")


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
    os_release_file = "/etc/os-release"
    if not path.exists(os_release_file):
        return None
    with open(os_release_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "VERSION_ID=" not in line:
                continue
            quote_wrapped_version = line.split("=")[1]
            version_str = quote_wrapped_version.replace('"', "").replace("\n", "")
            try:
                return int(version_str)
            except ValueError:
                pass


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


def get_internal_ip(iface=NetworkInterface.wlan0.name) -> str:
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
    return get_systemd_enabled_state("ssh")


def get_vnc_enabled_state() -> bool:
    return get_systemd_enabled_state("vncserver-x11-serviced.service")


def get_pt_further_link_enabled_state() -> bool:
    return get_systemd_enabled_state("further-link.service")


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
    operstate_file = f"/sys/class/net/{interface_name}/operstate"
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


def get_address_for_connected_device_dhcpcd() -> []:
    try:
        leases_file = "/var/lib/dhcp/dhcpd.leases"
        leases = ""
        if Path(leases_file).exists():
            leases = IscDhcpLeases(leases_file).get_current().values()
    except Exception as e:
        logger.error(f"Error reading dhcpd leases: {e}")
        return ""

    leases = list(leases)
    leases.reverse()
    return leases


@dataclass
class DnsmasqLease:
    timestamp: str = ""
    mac: str = ""
    ip: str = ""
    host: str = ""
    id: str = ""


def get_dnsmasq_leases(iface: str) -> []:

    def parse_dnsmasq_leases_line(line):
        pattern = r"(\d{10})\s((?:[a-zA-Z0-9]{2}[:-]){5}[a-zA-Z0-9]{2})\s((?:[0-9]{1,3}\.){3}[0-9]{1,3})\s(\S+)\s(\S+)"
        # comment = r"^\s*[//|#]"
        regex_match = re.match(pattern, line)

        if regex_match and len(regex_match.groups()) == 5:
            groups = regex_match.groups()
        else:
            return None

        return DnsmasqLease(
            timestamp=groups[0],
            mac=groups[1],
            ip=groups[2],
            host=groups[3],
            id=groups[4],
        )

    file = f"/var/lib/NetworkManager/dnsmasq-{iface}.leases"
    leases = []
    try:
        with open(file) as f:
            for line in f.readlines():
                lease = parse_dnsmasq_leases_line(line)
                if lease:
                    leases.append(lease)
    except Exception as e:
        logger.debug(f"Error reading dnsmasq leases: {e}")

    return leases


def get_address_for_connected_device(
    network: Union[None, IPv4Network, IPv6Network] = None
) -> str:

    if (
        run_command("systemctl is-active dhcpcd", check=False, timeout=5).strip()
        == "active"
    ):
        leases = get_address_for_connected_device_dhcpcd()
    else:
        leases = []
        for iface in (NetworkInterface.wlan_ap0.name, NetworkInterface.ptusb0.name):
            leases += get_dnsmasq_leases(iface)

    for lease in leases:
        if network and ip_address(lease.ip) not in network:
            continue

        def command_succeeds(cmd, timeout):
            try:
                run_command(cmd, timeout=timeout, check=True, log_errors=False)
                return True
            except Exception:
                return False

        # Windows machines won't respond to ping requests by default. Using arping
        # helps us on that case, but since it takes ~1.5s, it's used as a fallback
        if command_succeeds(f"ping -c1 {lease.ip}", 0.1) or command_succeeds(
            f"arping -c1 {lease.ip}", 2
        ):
            return lease.ip

    return ""


def get_address_for_ptusb_connected_device() -> str:
    if interface_is_up(NetworkInterface.ptusb0.name):
        return get_address_for_connected_device(
            network=InterfaceNetworkData(NetworkInterface.ptusb0.name).network
        )
    return ""


def get_address_for_ap_connected_device() -> str:
    if interface_is_up(NetworkInterface.wlan_ap0.name):
        return get_address_for_connected_device(
            network=InterfaceNetworkData(NetworkInterface.wlan_ap0.name).network
        )
    return ""


def is_connected_to_internet() -> bool:
    try:
        run_command("ping -c1 8.8.8.8", timeout=2, check=True, log_errors=False)
        return True
    except Exception:
        return False


def get_pi_top_ip():
    for iface in (NetworkInterface.wlan0, NetworkInterface.eth0):
        try:
            ip = ip_address(get_internal_ip(iface.name))
            return ip.exploded
        except ValueError:
            pass

    # ptusb0 & wlan_ap0 always have an IP address; check is performed differently
    for iface in (NetworkInterface.ptusb0, NetworkInterface.wlan_ap0):
        try:
            iface_data = InterfaceNetworkData(iface.name)
            if (
                interface_is_up(iface.name)
                and len(get_address_for_connected_device(network=iface_data.network))
                > 0
            ):
                return iface_data.ip.exploded
        except Exception:
            pass

    return ""
