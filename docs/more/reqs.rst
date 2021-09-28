------------
Requirements
------------

The following Debian packages are required for this library to work:

.. table::
    :widths: 30 70

    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | Package Name              | Usage                                                                                                                 |
    +===========================+=======================================================================================================================+
    | ``alsa-utils``            | Used for configuring the system audio; such as setting the correct audio card when connecting a pi-topSPEAKER.        |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``coreutils``             | Used to perform basic OS operations and commands; such as ``ls`` and ``chmod``                                        |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``fonts-droid-fallback``  | Minimum essential font used by the OLED screen.                                                                       |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``i2c-tools``             | Communicate with pi-top I2C devices.                                                                                  |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``pi-topd``               | Allows communication with pi-top's hub; such as getting battery state.                                                |
    |                           | This package installs a ``systemd`` service that needs to be running for this library to work properly                |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``raspi-config``          | Required to communicate and set parameters to the Raspberry Pi.                                                       |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
