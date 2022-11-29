from pitop.common.command_runner import run_command, run_command_background
from pitop.common.current_session_info import get_first_display
from pitop.common.sys_info import is_connected_to_internet

from ..formatter import StdoutFormat


class Links:
    ONLINE_BASE_URI = "https://docs.pi-top.com/python-sdk/"
    LOCAL_URI = "/usr/share/doc/python3-pitop/html/index.html"
    KNOWLEDGE_BASE_URI = "https://knowledgebase.pi-top.com/"
    FORUM_URI = "https://forum.pi-top.com/"

    def _is_doc_package_installed(self):
        try:
            run_command(
                "dpkg -l python3-pitop-doc", timeout=3, check=True, log_errors=False
            )
            return True
        except Exception:
            return False

    def __get_online_sdk_docs_url(self):
        try:
            return (
                self.ONLINE_BASE_URI
                + "en/v"
                + run_command(
                    "dpkg -s python3-pitop", timeout=10, check=True, log_errors=False
                )
                .split("\n")[8]
                .split()[1]
            )
        except Exception:
            return self.ONLINE_BASE_URI

    def get_docs_url(self):
        if is_connected_to_internet():
            return self.__get_online_sdk_docs_url()
        elif self._is_doc_package_installed():
            return self.LOCAL_URI
        else:
            raise Exception(
                "Not connected to internet and python3-pitop-doc not installed.\n"
                + "Please, connect to the internet or install the documentation package via 'sudo apt install python3-pitop-doc'"
            )

    def print_docs(self):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("DOCS")
        StdoutFormat.print_checkbox_line(
            "pi-top Python SDK documentation",
            "online version, recommended",
            self.__get_online_sdk_docs_url(),
            is_connected,
        )
        StdoutFormat.print_checkbox_line(
            "pi-top Python SDK documentation",
            "offline version",
            self.LOCAL_URI,
            self._is_doc_package_installed(),
        )

    def print_other(self):
        is_connected = is_connected_to_internet()
        StdoutFormat.print_header("OTHER")
        StdoutFormat.print_checkbox_line(
            "Knowledge Base",
            "Find answers to commonly asked questions",
            self.KNOWLEDGE_BASE_URI,
            is_connected,
        )
        StdoutFormat.print_checkbox_line(
            "Forum",
            "Discuss and search through support topics.",
            self.FORUM_URI,
            is_connected,
        )

    def open_docs_in_browser(self):
        display = get_first_display()
        if display is None:
            raise Exception(
                "There isn't a display available to open the documentation."
            )
        url = self.get_docs_url()
        run_command_background(f"x-www-browser {url}")
