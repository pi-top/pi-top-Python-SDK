import subprocess
import netifaces
from os import uname
from os import path
from fractions import Fraction
from isc_dhcp_leases import IscDhcpLeases

from pitop.core.formatting import bytes2human, remove_prefix
from pitop.core.logger import PTLogger
from pitop.core.command_runner import run_command


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
                except ValueError as ex:
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


def get_battery_capacity():
    try:
        response = (
            str(
                subprocess.check_output(
                    ["pt-battery", "-c"], stderr=subprocess.STDOUT
                ).decode("utf-8")
            ).strip()
        )
    except FileNotFoundError:
        response = "pt-battery Error"
    except subprocess.CalledProcessError as e:
        response = str(e.output.decode("utf-8"))
        if "Error" not in response:
            response = "Error: " + str(e.output.decode("utf-8"))
    except:
        response = "Unknown Error"

    return response


def get_battery_charging_state():
    try:
        charging_state = subprocess.check_output(
            ["pt-battery", "-s"], stderr=subprocess.STDOUT
        ).decode("utf-8")
        response = charging_state
    except FileNotFoundError:
        response = "pt-battery Error"
    except subprocess.CalledProcessError as e:
        response = str(e.output.decode("utf-8"))
        if "Error" not in response:
            response = "Error: " + str(e.output.decode("utf-8"))
    except:
        response = "Unknown Error"

    return response


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
    except:
        return "Addresses Not Found"

    try:
        inet_addrs = addrs[netifaces.AF_INET][0]
    except:
        return "Internet Addresses Not Found"

    try:
        internal_ip = inet_addrs['addr']
    except:
        return "IP Not Found"

    return internal_ip


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


def get_host_device_version():
    try:
        with open("/etc/pi-top/pt-device-manager/device_version", "r") as device_version_file:
            return device_version_file.readline().strip()
    except IOError:
        return "Error getting valid pi-top version from device version file"


def interface_is_up(interface_name):
    operstate_file = "/sys/class/net/" + interface_name + "/operstate"
    if not path.exists(operstate_file):
        return False

    contents = ""
    with open(operstate_file, "r") as file:
        contents = file.read()

    return "up" in contents


def get_address_for_ptusb_connected_device():
    if interface_is_up("ptusb0"):
        for lease in IscDhcpLeases(
                '/var/lib/dhcp/dhcpd.leases').get_current().values():
            try:
                run_command("ping -c1 {}".format(lease.ip),
                            timeout=0.1, check=True)
                PTLogger.debug(
                    "Leased IP address {} is connected.".format(lease.ip))
                return lease.ip
            except Exception as e:
                PTLogger.debug(
                    "Leased IP address {} is not connected.".format(lease.ip))
                continue
    return ""
