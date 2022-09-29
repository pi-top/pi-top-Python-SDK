import re


class DigitalComponentChecks:
    """Performs basic checks on validity of user-specified port."""

    def __init__(self, port_name):
        self.port_name = port_name

        # For the sake of a helpful error message, first check if the port is actually a valid port of any kind
        if not re.search("^D[0-7]$|^A[0-3]$", self.port_name):
            raise ValueError(
                f"{self.port_name} is not a valid port name. An example of a valid port name is D0"
            )

        # Then, in this case, verify the port is digital not analog
        if re.search("^A[0-3]$", self.port_name):
            raise ValueError(
                f"Can't use analog port {self.port_name} for digital component. Try using a digital port, such as D0"
            )
