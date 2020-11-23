==========================
 Command-Line Tools (CLI)
==========================

--------------------
pt-config
--------------------

Utility to interact with pi-top hardware.

.. code-block:: bash

    pt-config [-h] {brightness,device,host,battery,oled} ...

Where:

-h, --help
    Show a help message and exits

{brightness,device,host,battery,oled}
    battery:
        Get battery information from a pi-top.

    brightness:
        Communicate and control the device's screen brightness

    devices:
        Get information about device and attached pi-top hardware

    host:
        Returns the name of the host pi-top device

    oled:
        Quickly display text in pi-top [4]'s OLED screen


pt-config battery
=========================

If the pi-top device has an internal battery, it will report it's status.

.. code-block:: bash

    pt-battery [-h] [-s] [-c] [-t] [-w] [-v]


Where:

-h, --help
    Show a help message and exits

-s, --charging-state
    Optional. Return the charging state of the battery as an number, where:

    * -1: No pi-top battery detected

    * 0: Discharging

    * 1: Charging

    * 2: Full battery

-c, --capacity
    Optional. Get battery capacity percentage %

-t, --time-remaining
    Optional. Get the time (in minutes) to full or time to empty based on the charging state

-w, --wattage
    Optional. Get the wattage (mAh) of the battery

-v, --verbose
    If no argument is provided, this option will be used by default.

    Report all the information available about the battery (charging state, capacity, time remaining
    and wattage)

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-config battery
    Charging State: 0
    Capacity: 42
    Time Remaining: 104
    Wattage: -41

pt-config brightness
=========================

On pi-top devices with a screen, it allows to query and control its brightness.

Running `pt-brightness` on its own will report back the current brightness value.

.. code-block:: bash

    pt-config brightness [-h] [-b {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}] [-i]
                     [-d] [-l {0,1}] [-t TIMEOUT] [-v]


Where:

-h, --help
    Show a help message and exits

-b {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}, --brightness_value {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}
    Set screen brightness level [1-10] on pi-topHUB, or
    [1-16] or pi-topHUB v2

-i, --increment_brightness
    Increment screen brightness level

-d, --decrement_brightness
    Decrement screen brightness level

-l {0,1}, --backlight {0,1}
    Set the screen backlight state [0-1]

-t TIMEOUT, --timeout TIMEOUT
    Set the timeout before the screen blanks in seconds (0
    to disable)

-v, --verbose
    Increase output verbosity


Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-config brightness
    16

pt-config devices
===================

Finds useful information about the system and the attached devices that are being managed by `pt-device-manager`.

This command doesn't receive arguments.

.. code-block:: bash

    pt-config devices

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-config devices
    Host device: pi-top [4]
    pi-top Touchscreen: not connected
    pi-top Keyboard: not connected
    Upgradable device connected: pi-top [4] Hub (v5.3)
    Upgradable device connected: pi-top [4] Expansion Plate (v21.5)

pt-config host
==================

Returns the pi-top host device name where the command is being run.

This command doesn't receive arguments.

.. code-block:: bash

    pt-config host

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # on a pi-top [4]
    pi@pi-top:~ $ pt-config host
    pi-top [4]

.. code-block:: bash

    # on a pi-top [3]
    pi@pi-top:~ $ pt-config host
    pi-top [3]

pt-config oled
==================

Display text directly into pi-top [4]'s OLED screen.

.. code-block:: bash

    pt-config oled [-h] [--timeout TIMEOUT] [--font-size FONT_SIZE] text

Where:

text
    set the text to write to screen

-h, --help
    Show a help message and exits

--timeout TIMEOUT
    set the timeout in seconds

--font-size FONT_SIZE
    set the font size

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pt-config oled "hey there!" --timeout 5


--------------------
Deprecated CLI
--------------------

The following is a list of deprecated CLI tools. They continue to work, but will print
a message prompting to move to the new CLI `pt-config`.

pt-battery
==================

To learn about the command arguments, check `pt-config battery`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-battery
    Note: Use of the 'pt-battery' is now deprecated. Please use 'pt-config battery' instead.
    Charging State: 0
    Capacity: 42
    Time Remaining: 104
    Wattage: -41


pt-brightness
==================

To learn about the command arguments, check `pt-config brightness`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-brightness
    Note: Use of the 'pt-brightness' is now deprecated. Please use 'pt-config brightness' instead.
    16

pt-devices
==================

To learn about the command arguments, check `pt-config devices`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-devices
    Note: Use of the 'pt-device' is now deprecated. Please use 'pt-config device' instead.
    Host device: pi-top [4]
    pi-top Touchscreen: not connected
    pi-top Keyboard: not connected
    Upgradable device connected: pi-top [4] Hub (v5.3)
    Upgradable device connected: pi-top [4] Expansion Plate (v21.5)


pt-host
==============

To learn about the command arguments, check `pt-config host`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # on a pi-top [4]
    pi@pi-top:~ $ pt-host
    Note: Use of the 'pt-host' is now deprecated. Please use 'pt-config host' instead.
    pi-top [4]

pt-oled
============

To learn about the command arguments, check `pt-config oled`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-oled "hey there!" --timeout 5
    Note: Use of the 'pt-oled' is now deprecated. Please use 'pt-config oled' instead.
