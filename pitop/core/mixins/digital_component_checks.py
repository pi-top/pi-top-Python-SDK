
valid_digital_ports = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]

class DigitalComponentChecks:
    """Performs basic checks on validity of user-specified port"""

    def __init__(self, port_name):
        self.port_name = port_name

        if port_name not in valid_digital_ports:
            raise ValueError(f"{port_name} is not a valid port name. An example of a valid port name is D0")

        if not port_name.startswith("D"):
            raise ValueError(f"{port_name} is not a valid port type for a button. Try using a digital port, such as D0")
