==========================
 Command-Line Tools (CLI)
==========================

----------------
'pi-top' Command
----------------

Utility to interact with pi-top hardware.

.. code-block:: bash

    pi-top [-h] {brightness,devices,host,battery,oled} ...

Where:

-h, --help
    Show a help message and exits

{brightness,devices,host,battery,oled}
    battery:
        Get battery information from a pi-top

    brightness:
        Query and change the device's screen brightness

    devices:
        Get information about device and attached pi-top hardware

    host:
        Returns the name of the host pi-top device

    oled:
        Quickly display text in pi-top [4]'s OLED screen


pi-top battery
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

    pi@pi-top:~ $ pi-top battery
    Charging State: 0
    Capacity: 42
    Time Remaining: 104
    Wattage: -41

pi-top display
=========================

On pi-top devices with a screen, it allows to control different display settings.

.. code-block:: bash

    pi-top display [-h] {brightness,backlight,timeout}

Where:

-h, --help
    Show a help message and exits

brightness
    Control display brightness

backlight
    Control display backlight

timeout
    Set the timeout before the screen blanks in seconds (0 to disable)


pi-top display brightness
~~~~~~~~~~~~~~~~~~~~~~~~~~

Request or change the value of the display's brightness.

Note: this only works for the original pi-top, pi-topCEED and pi-top [3]. The pi-top [4] Full HD Touch Display uses hardware buttons to control the brightness, and is not controllable via this SDK.

.. code-block:: bash

    pi-top display brightness [-h] [-v] [-i] [-d]
                                 [brightness_value]

Where:

-h, --help
    Show a help message and exits

-v, --verbose
    Increase verbosity of output

-i, --increment_brightness
    Increment screen brightness level

-d, --decrement_brightness
    Decrement screen brightness level

brightness_value
    Set screen brightness level [1-10] on pi-topHUB, or
    [1-16] or pi-topHUB v2


Using `pi-top display brightness` without arguments will return the current brightness value.

Note that the `brightness_value` range differs for different devices: for pi-top [3] is from 0-16; pi-top [1] and CEED is 0-10.


Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pi-top display brightness
    16


pi-top display backlight
~~~~~~~~~~~~~~~~~~~~~~~~~~

Using `pi-top display backlight` without arguments will return the current backlight status.

.. code-block:: bash

    pi-top display backlight [-h] [-v] [{0,1}]

Where:

-h, --help
    Show a help message and exits

-v, --verbose
    Increase verbosity of output

{0,1}
    Set the screen backlight state [0-1]

pi-top display blank_time
~~~~~~~~~~~~~~~~~~~~~~~~~~

Set the time before the screen goes blank on inactivity periods.

Using `pi-top display blank_time` without arguments will return the screen's timeout value.

.. code-block:: bash

    pi-top display timeout [-h] [-v] [timeout_value]

Where:

-h, --help
    Show a help message and exits

-v, --verbose
    Increase verbosity of output

timeout_value
    Timeout value in seconds. Set to 0 to disable.


pi-top devices
===================

Finds useful information about the system and the attached devices that are being managed by `pt-device-manager`.

Running `pi-top devices` on its own will report back the current brightness value.

.. code-block:: bash

    pi-top devices [-h] [--quiet] [--name-only] {hub,peripherals}

Where:

-h, --help
    Show a help message and exits

--quiet, -q
    Display only the connected devices

--name-only, -n
    Display only the name of the devices, without further information

hub
    Get the name of the active pi-top device

peripherals
    Get information about attached pi-top peripherals

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pi-top devices
    HUB ===================================================
    pi-top [4] (v5.4)
    PERIPHERALS ===========================================
    [ ✓ ] pi-top [4] Expansion Plate (v21.5)
    [   ] pi-top Touchscreen
    [   ] pi-top Keyboard
    [   ] pi-topPULSE
    [   ] pi-topSPEAKER (v1) - Left channel
    [   ] pi-topSPEAKER (v1) - Right channel
    [   ] pi-topSPEAKER (v1) - Mono
    [   ] pi-topSPEAKER (v2)

.. code-block:: bash

    pi@pi-top:~ $ pt devices peripherals
    [ ✓ ] pi-top [4] Expansion Plate (v21.5)
    [   ] pi-top Touchscreen
    [   ] pi-top Keyboard
    [   ] pi-topPULSE
    [   ] pi-topSPEAKER (v1) - Left channel
    [   ] pi-topSPEAKER (v1) - Right channel
    [   ] pi-topSPEAKER (v1) - Mono
    [   ] pi-topSPEAKER (v2)

.. code-block:: bash

    pi@pi-top:~ $ pt devices hub --name-only
    pi-top [4]

pi-top oled
==================

Display text directly into pi-top [4]'s OLED screen.

.. code-block:: bash

    pi-top oled [-h] [--timeout TIMEOUT] [--font-size FONT_SIZE] text

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

    pi-top oled "hey there!" --timeout 5


--------------------
Deprecated CLI
--------------------

The following is a list of deprecated CLI tools. They continue to work, but will print
a message prompting to move to the new CLI `pi-top`.

pt-battery
==================

To learn about the command arguments, check `pi-top battery`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-battery
    Note: Use of the 'pt-battery' is now deprecated. Please use 'pi-top battery' instead.
    Charging State: 0
    Capacity: 42
    Time Remaining: 104
    Wattage: -41


pt-brightness
==================

To learn about the command arguments, check `pi-top display brightness`.

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-brightness
    Note: Use of the 'pt-brightness' is now deprecated. Please use 'pi-top display brightness' instead.
    16

pt-devices
==================

To learn about the command arguments, check `pi-top devices`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-devices
    Note: Use of the 'pt-device' is now deprecated. Please use 'pi-top device' instead.
    Host device: pi-top [4]
    pi-top Touchscreen: not connected
    pi-top Keyboard: not connected
    Upgradable device connected: pi-top [4] Hub (v5.3)
    Upgradable device connected: pi-top [4] Expansion Plate (v21.5)


pt-host
==============

Prints the name of the active pi-top device. Check `pi-top devices`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # on a pi-top [4]
    pi@pi-top:~ $ pt-host
    Note: Use of the 'pt-host' is now deprecated. Please use 'pi-top devices hub' instead.
    pi-top [4]

pt-oled
============

To learn about the command arguments, check `pi-top oled`_

Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pi@pi-top:~ $ pt-oled "hey there!" --timeout 5
    Note: Use of the 'pt-oled' is now deprecated. Please use 'pi-top oled' instead.
