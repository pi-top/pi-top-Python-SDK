from ipaddress import ip_address
from unittest import TestCase
from unittest.mock import Mock, call, mock_open, patch


class SysInfoTestCase(TestCase):
    def test_network_interfaces_enum(self):
        from pitop.common.sys_info import NetworkInterface

        ifaces = ("eth0", "wlan0", "wlan_ap0", "ptusb0")
        for iface in NetworkInterface:
            assert iface.name in ifaces

    @patch("pitop.common.sys_info.uname")
    def test_is_pi_architecture_verification(self, uname_mock):
        response_mock = Mock()
        uname_mock.return_value = response_mock

        from pitop.common.sys_info import is_pi

        for machine, expected_value in (
            ("amd64", False),
            ("anything", False),
            ("armv7l", True),
            ("aarch64", True),
        ):
            response_mock.machine = machine
            assert is_pi() is expected_value

    @patch("pitop.common.sys_info.open", new_callable=mock_open())
    def test_debian_version_checks_version_file(self, open_mock):
        from pitop.common.sys_info import get_debian_version

        get_debian_version()
        open_mock.assert_called_with("/etc/debian_version", "r")

    @patch("pitop.common.sys_info.path")
    def test_debian_version_checks_if_version_file_exists(self, path_mock):
        path_mock.exists.return_value = False
        from pitop.common.sys_info import get_debian_version

        assert get_debian_version() is None

    @patch(
        "pitop.common.sys_info.open", new_callable=mock_open(), read_data="bullseye/sid"
    )
    def test_debian_version_returns_file_content(self, _):
        from pitop.common.sys_info import get_debian_version

        get_debian_version() == "bullseye/sid"

    @patch(
        "pitop.common.sys_info.open", new_callable=mock_open, read_data="VERSION_ID=99"
    )
    def test_debian_maj_version_checks_os_release_file(self, open_mock):
        from pitop.common.sys_info import get_maj_debian_version

        get_maj_debian_version()
        open_mock.assert_called_with("/etc/os-release", "r")

    @patch(
        "pitop.common.sys_info.open", new_callable=mock_open, read_data="VERSION_ID=99"
    )
    def test_debian_maj_version_content(self, _):
        from pitop.common.sys_info import get_maj_debian_version

        assert get_maj_debian_version() == 99

    @patch("pitop.common.sys_info.path")
    def test_debian_maj_version_checks_if_version_file_exists(self, path_mock):
        path_mock.exists.return_value = False
        from pitop.common.sys_info import get_maj_debian_version

        assert get_maj_debian_version() is None

    @patch("pitop.common.sys_info.check_output")
    def test_network_strength_runs_iwconfig(self, check_output_mock):
        from pitop.common.sys_info import get_network_strength

        iface = "wlan0"
        get_network_strength(iface)
        check_output_mock.assert_called_with(["iwconfig", iface])

    @patch("pitop.common.sys_info.check_output", side_effect=FileNotFoundError)
    def test_network_strength_on_check_output_error(self, _):
        from pitop.common.sys_info import get_network_strength

        assert get_network_strength("wlan0") == "-1%"

    @patch("pitop.common.sys_info.check_output")
    def test_network_strength_parse_iwconfig(self, check_output_mock):
        check_output_mock.return_value = b"""
        wlan0     IEEE 802.11  ESSID:"my network"
          Mode:Managed  Frequency:2.427 GHz  Access Point: 44:10:32:F1:57:2A
          Bit Rate=65 Mb/s   Tx-Power=31 dBm
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:off
          Link Quality=1/100  Signal level=-62 dBm
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:0  Invalid misc:0   Missed beacon:0
        """
        from pitop.common.sys_info import get_network_strength

        iface = "wlan0"
        assert get_network_strength(iface) == "1%"

    @patch("pitop.common.sys_info.check_output")
    def test_network_strength_parse_iwconfig_without_expected_response(
        self, check_output_mock
    ):
        check_output_mock.return_value = b"this is an unexpected response"
        from pitop.common.sys_info import get_network_strength

        iface = "wlan0"
        assert get_network_strength(iface) == "-1%"

    @patch("pitop.common.sys_info.check_output")
    def test_wifi_network_ssid_runs_iwgetid(self, check_output_mock):
        check_output_mock.return_value = b"my ssid"
        from pitop.common.sys_info import get_wifi_network_ssid

        assert get_wifi_network_ssid() == "my ssid"

    @patch("pitop.common.sys_info.check_output", side_effect=FileNotFoundError)
    def test_wifi_network_ssid_on_error(self, _):
        from pitop.common.sys_info import get_wifi_network_ssid

        assert get_wifi_network_ssid() == "Error"

    def test_internal_ip_on_unknown_interface(self):
        from pitop.common.sys_info import get_internal_ip

        invalid_iface = "not a valid interface"
        assert get_internal_ip(invalid_iface) == f"{invalid_iface} Not Found"

    @patch("pitop.common.sys_info.netifaces")
    def test_internal_ip_on_interface_on_ifaddresses_error(self, netifaces_mock):
        netifaces_mock.interfaces.return_value = "wlan0"
        netifaces_mock.ifaddresses.side_effect = Exception

        from pitop.common.sys_info import get_internal_ip

        assert get_internal_ip("wlan0") == "Addresses Not Found"

    @patch("pitop.common.sys_info.netifaces")
    def test_internal_ip_on_interface_with_invalid_ifaddresses_response(
        self, netifaces_mock
    ):
        netifaces_mock.interfaces.return_value = "wlan0"
        netifaces_mock.ifaddresses.return_value = ""

        from pitop.common.sys_info import get_internal_ip

        assert get_internal_ip("wlan0") == "Internet Addresses Not Found"

    @patch("pitop.common.sys_info.netifaces")
    def test_internal_ip_on_interface_without_ip(self, netifaces_mock):
        from netifaces import AF_INET

        netifaces_mock.AF_INET = AF_INET
        netifaces_mock.interfaces.return_value = "wlan0"
        netifaces_mock.ifaddresses.return_value = {AF_INET: ["123"]}

        from pitop.common.sys_info import get_internal_ip

        assert get_internal_ip("wlan0") == "IP Not Found"

    @patch("pitop.common.sys_info.run_command")
    def test_start_systemd_service_command(self, run_command_mock):
        from pitop.common.sys_info import start_systemd_service

        start_systemd_service("pt-miniscreen")
        run_command_mock.assert_called_once_with(
            "systemctl start pt-miniscreen", timeout=20, check=True, log_errors=False
        )

    @patch("pitop.common.sys_info.run_command")
    def test_stop_systemd_service_command(self, run_command_mock):
        from pitop.common.sys_info import stop_systemd_service

        stop_systemd_service("pt-miniscreen")
        run_command_mock.assert_called_once_with(
            "systemctl stop pt-miniscreen", timeout=20, check=False, log_errors=False
        )

    @patch("pitop.common.sys_info.run_command")
    def test_systemd_active_state_command(self, run_command_mock):
        from pitop.common.sys_info import get_systemd_active_state

        get_systemd_active_state("pt-miniscreen")
        run_command_mock.assert_called_once_with(
            "systemctl is-active pt-miniscreen", timeout=10, log_errors=False
        )

    @patch("pitop.common.sys_info.run_command", side_effect=Exception)
    def test_systemd_active_state_response_on_error(self, run_command_mock):
        from pitop.common.sys_info import get_systemd_active_state

        assert get_systemd_active_state("pt-miniscreen") == "Unknown Error"

    @patch("pitop.common.sys_info.check_output")
    def test_systemd_enabled_state_command(self, check_output_mock):
        from pitop.common.sys_info import get_systemd_enabled_state

        get_systemd_enabled_state("pt-miniscreen")
        check_output_mock.assert_called_once_with(
            ["systemctl", "is-enabled", "pt-miniscreen"]
        )

    @patch("pitop.common.sys_info.check_output", side_effect=Exception)
    def test_systemd_enabled_state_response_on_error(self, check_output_mock):
        from pitop.common.sys_info import get_systemd_enabled_state

        assert get_systemd_enabled_state("pt-miniscreen") == "Unknown error"

    @patch("pitop.common.sys_info.get_systemd_enabled_state")
    def test_get_systemd_enabled_state_based_functions(
        self, get_systemd_enabled_state_mock
    ):
        from pitop.common.sys_info import (
            get_pt_further_link_enabled_state,
            get_ssh_enabled_state,
            get_vnc_enabled_state,
        )

        for func, service in (
            (get_ssh_enabled_state, "ssh"),
            (get_vnc_enabled_state, "vncserver-x11-serviced.service"),
            (get_pt_further_link_enabled_state, "further-link.service"),
        ):
            func()
            get_systemd_enabled_state_mock.assert_called_with(service)

    @patch("pitop.common.sys_info.path")
    @patch("pitop.common.sys_info.open", new_callable=mock_open())
    def test_interface_is_up_checks_version_file(self, open_mock, path_mock):
        from pitop.common.sys_info import interface_is_up

        path_mock.exists.return_value = True
        interface_name = "wlan0"
        interface_is_up(interface_name)
        open_mock.assert_called_with(f"/sys/class/net/{interface_name}/operstate", "r")

    @patch("pitop.common.sys_info.path")
    def test_interface_is_up_checks_if_version_file_exists(self, path_mock):
        path_mock.exists.return_value = False
        from pitop.common.sys_info import interface_is_up

        assert interface_is_up("wlan0") is False

    @patch("pitop.common.sys_info.path")
    @patch("pitop.common.sys_info.open", new_callable=mock_open, read_data="up")
    def test_interface_is_up_returns_file_content(self, open_mock, path_mock):
        path_mock.exists.return_value = True
        from pitop.common.sys_info import interface_is_up

        assert interface_is_up("wlan0") is True

    @patch("pitop.common.sys_info.run_command")
    def test_pings_to_determine_internet_connection_status(self, run_command_mock):
        from pitop.common.sys_info import is_connected_to_internet

        is_connected_to_internet()
        run_command_mock.assert_called_once_with(
            "ping -c1 8.8.8.8", timeout=2, check=True, log_errors=False
        )

    # get_address_for_connected_device

    @patch("pitop.common.sys_info.IscDhcpLeases")
    def test_get_address_for_connected_device_checks_dhcp_leases(
        self, isc_dhcp_leases_mock
    ):
        from pitop.common.sys_info import get_address_for_connected_device

        get_address_for_connected_device()
        isc_dhcp_leases_mock.assert_called_with("/var/lib/dhcp/dhcpd.leases")

    @patch("pitop.common.sys_info.run_command")
    @patch("pitop.common.sys_info.IscDhcpLeases")
    def test_get_address_for_connected_device_pings_leased_ips(
        self, isc_dhcp_leases_mock, run_command_mock
    ):
        ip = "192.168.64.1"
        lease = Mock()
        lease.ip = ip
        leases = [lease]

        values_mock = Mock()
        values_mock.values.return_value = leases
        get_current_mock = Mock()
        get_current_mock.get_current.return_value = values_mock
        isc_dhcp_leases_mock.return_value = get_current_mock
        isc_dhcp_leases_mock().get_current().values()

        from pitop.common.sys_info import get_address_for_connected_device

        get_address_for_connected_device()

        run_command_mock.assert_called_once_with(
            "ping -c1 192.168.64.1", timeout=0.1, check=True, log_errors=False
        )

    @patch("pitop.common.sys_info.run_command")
    @patch("pitop.common.sys_info.IscDhcpLeases")
    def test_get_address_for_connected_device_arpings_if_ping_failed(
        self, isc_dhcp_leases_mock, run_command_mock
    ):
        ip = "192.168.64.1"
        lease = Mock()
        lease.ip = ip
        leases = [lease]

        values_mock = Mock()
        values_mock.values.return_value = leases
        get_current_mock = Mock()
        get_current_mock.get_current.return_value = values_mock
        isc_dhcp_leases_mock.return_value = get_current_mock
        isc_dhcp_leases_mock().get_current().values()

        def run_command_side_effect(command, timeout):
            return "arping" in command

        run_command_mock.side_effect = run_command_side_effect

        from pitop.common.sys_info import get_address_for_connected_device

        get_address_for_connected_device()

        assert run_command_mock.call_count == 2
        run_command_mock.assert_has_calls(
            [
                call(
                    "arping -c1 192.168.64.1", timeout=2, check=True, log_errors=False
                ),
                call(
                    "ping -c1 192.168.64.1", timeout=0.1, check=True, log_errors=False
                ),
            ],
            any_order=True,
        )

    @patch("pitop.common.sys_info.run_command")
    @patch("pitop.common.sys_info.IscDhcpLeases")
    def test_get_address_for_connected_device_on_no_response(
        self, isc_dhcp_leases_mock, run_command_mock
    ):
        ip = ""
        lease = Mock()
        lease.ip = ip
        leases = [lease]

        values_mock = Mock()
        values_mock.values.return_value = leases
        get_current_mock = Mock()
        get_current_mock.get_current.return_value = values_mock
        isc_dhcp_leases_mock.return_value = get_current_mock
        isc_dhcp_leases_mock().get_current().values()

        run_command_mock.side_effect = lambda command, timeout: False

        from pitop.common.sys_info import get_address_for_connected_device

        assert get_address_for_connected_device() == ""
        assert run_command_mock.call_count == 2

    @patch("pitop.common.sys_info.ip_address")
    @patch("pitop.common.sys_info.ip_network")
    @patch("pitop.common.sys_info.interface_is_up")
    @patch("pitop.common.sys_info.get_address_for_connected_device")
    def test_get_address_for_connected_device_based_functions(
        self,
        get_address_for_connected_device_mock,
        interface_is_up_mock,
        ip_address_mock,
        ip_network_mock,
    ):
        interface_is_up_mock.side_effect = lambda _: True
        from pitop.common.sys_info import (
            get_address_for_ap_connected_device,
            get_address_for_ptusb_connected_device,
        )

        for func in (
            get_address_for_ptusb_connected_device,
            get_address_for_ap_connected_device,
        ):
            func()

        assert get_address_for_connected_device_mock.call_count == 2

    @patch("pitop.common.sys_info.ip_address")
    @patch("pitop.common.sys_info.ip_network")
    @patch("pitop.common.sys_info.interface_is_up")
    @patch("pitop.common.sys_info.get_address_for_connected_device")
    def test_get_address_for_connected_device_based_functions_check_interface_first(
        self,
        get_address_for_connected_device_mock,
        interface_is_up_mock,
        ip_address_mock,
        ip_network_mock,
    ):
        interface_is_up_mock.side_effect = lambda _: True
        from pitop.common.sys_info import (
            get_address_for_ap_connected_device,
            get_address_for_ptusb_connected_device,
        )

        for func in (
            get_address_for_ptusb_connected_device,
            get_address_for_ap_connected_device,
        ):
            func()

        assert interface_is_up_mock.call_count == 2

    @patch("pitop.common.sys_info.get_address_for_connected_device")
    @patch("pitop.common.sys_info.get_internal_ip")
    def test_get_pi_top_ip_if_wlan0_has_ip(
        self, get_internal_ip_mock, get_address_for_connected_device_mock
    ):
        ip = "192.168.100.44"
        get_internal_ip_mock.return_value = ip

        from pitop.common.sys_info import get_pi_top_ip

        assert get_pi_top_ip() == ip
        assert get_address_for_connected_device_mock.call_count == 0

    @patch("pitop.common.sys_info.InterfaceNetworkData")
    @patch("pitop.common.sys_info.interface_is_up")
    @patch("pitop.common.sys_info.get_address_for_connected_device")
    @patch("pitop.common.sys_info.get_internal_ip")
    def test_get_pi_top_ip_if_ptusb0_has_ip(
        self,
        get_internal_ip_mock,
        get_address_for_connected_device_mock,
        interface_is_up_mock,
        InterfaceNetworkDataMock,
    ):
        ip = "192.168.64.10"
        interface_is_up_mock.return_value = True
        get_internal_ip_mock.side_effect = ValueError
        get_address_for_connected_device_mock.return_value = ip

        obj_mock = Mock()
        obj_mock.ip = ip_address(ip)
        obj_mock.name = "ptusb0"
        obj_mock.network = "192.168.64.0/24"
        InterfaceNetworkDataMock.return_value = obj_mock

        from pitop.common.sys_info import get_pi_top_ip

        assert get_pi_top_ip() == ip
        assert get_address_for_connected_device_mock.call_count == 1

    @patch("pitop.common.sys_info.InterfaceNetworkData")
    @patch("pitop.common.sys_info.get_internal_ip")
    def test_get_pi_top_ip_fallback_response(
        self, get_internal_ip_mock, InterfaceNetworkDataMock
    ):
        get_internal_ip_mock.side_effect = ValueError
        InterfaceNetworkDataMock.side_effect = Exception

        from pitop.common.sys_info import get_pi_top_ip

        assert get_pi_top_ip() == ""
