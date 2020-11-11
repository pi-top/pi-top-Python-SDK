=====================================================
Command-Line Tools (CLI)
=====================================================

pt-battery
--------------------

If the pi-top device has an internal battery, it will report it's status.

Running `pt-battery` on its own will report all the available information about the battery.

Usage
~~~~~~~~~~~

.. code-block::

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
~~~~~~~~~~~

.. code-block::

    pi@pi-top:~ $ pt-battery
        Charging State: 0
        Capacity: 42
        Time Remaining: 104
        Wattage: -41



pt-brightness
--------------------

On pi-top devices with a screen, it allows to query and control its brightness.

Running `pt-brightness` on its own will report back the current brightness value.

Usage
~~~~~~~~~~~

.. code-block::

    pt-brightness [-h] [-b {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}] [-i]
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
~~~~~~~~~~~

.. code-block::

    pi@pi-top:~ $ pt-brightness
    16
    pi@pi-top:~ $ pt-brightness -b 10
    pi@pi-top:~ $ pt-brightness
    10
    pi@pi-top:~ $ pt-brightness -i
    pi@pi-top:~ $ pt-brightness
    11


pt-device
--------------------

Finds useful information about the system and the attached devices that are being managed by `pt-device-manager`.

Usage
~~~~~~~~~~~

This command doesn't receive arguments.

.. code-block::

    pt-devices


Example
~~~~~~~~~~~

.. code-block::

    pi@pi-top:~ $ pt-devices
        Devices and peripherals handled by pt-device-manager:
        OS release: 5.4.51-v7l+
        Host device is pi-top [4]


pt-host
--------------------

Returns the pi-top host device name where the command is being run.


Usage
~~~~~~~~~~~

This command doesn't receive arguments.

.. code-block::

    pt-host

Example
~~~~~~~~~~~

.. code-block::

    # on a pi-top [4]
    pi@pi-top:~ $ pt-host
    pi-top [4]

.. code-block::

    # on a pi-top [3]
    pi@pi-top:~ $ pt-host
    pi-top [3]


pt-oled
--------------------

Usage
~~~~~~~~~~~

Example
~~~~~~~~~~~

.. code-block::

    pt-oled
