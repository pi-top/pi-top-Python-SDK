class Error(Exception):
    """Base class for exceptions in this library."""

    pass


class DeviceNotFoundError(Error):
    """Exception raised when a device cannot be found."""


class DevicePermissionError(Error):
    """Exception raised when permission to access the device is denied."""


class DeviceAddressError(Error):
    """Exception raised when an invalid device address is detected."""


class DeviceDisplayModeError(Error):
    """Exception raised when an invalid device display mode is detected."""


class UnsupportedPlatform(Error):
    """Exception raised when trying to use the library on an incompatible
    system."""
