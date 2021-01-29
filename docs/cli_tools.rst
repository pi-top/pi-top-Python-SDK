==========================
 Command-Line Tools (CLI)
==========================

----------------
'pi-top' Command
----------------

Utility to interact with pi-top hardware.

.. code-block:: bash

    pi-top [-h] {battery,devices,display,support,imu,oled} ...

Where:

-h, --help
    Show a help message and exits

{battery,devices,display,help,imu,oled}
    battery:
        Get battery information from a pi-top

    devices:
        Get information about device and attached pi-top hardware

    display:
        Communicate and control the device's display

    support:
        Find support resources

    imu:
        Expansion Plate IMU utilities

    oled:
        Quickly display text in pi-top [4]'s OLED screen


pi-top battery
=========================

If the pi-top device has an internal battery, it will report its status.

.. code-block:: bash

    pi-top battery [-h] [-s] [-c] [-t] [-w] [-v]


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

Example:

.. code-block:: bash

    pi@pi-top:~ $ pi-top battery
    Charging State: 0
    Capacity: 42
    Time Remaining: 104
    Wattage: -41

pi-top display
=========================

This command provides a way to control different display settings on pi-top devices with a built-in screen.

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
    Set screen brightness level; [1-10] on pi-top [1] and pi-topCEED,
    [1-16] for pi-top [3]


Using `pi-top display brightness` without arguments will return the current brightness value.

Note that the `brightness_value` range differs for different devices: for pi-top [3] is from 0-16; pi-top [1] and CEED is 0-10.


Example:

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


Example:

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


pi-top imu
==================

Utility to calibrate the IMU included in the Expansion Plate.

.. code-block:: bash

    pi-top imu calibrate [-h] [-p PATH]

Where:

-h, --help
    Show a help message and exits

-p PATH, --path PATH
    Directory for storing calibration graph data


Example:

.. code-block:: bash

    pi-top imu calibrate --path /tmp



pi-top oled
==================

Configure and display text/images directly onto pi-top [4]'s OLED screen.

.. code-block:: bash

    pi-top oled [-h] {display,spi}

Where:


-h, --help
    Show a help message and exits

display
    Display text and images into the OLED

spi
    Control the SPI bus used by OLED



pi-top oled display
~~~~~~~~~~~~~~~~~~~~~~~~~~

Display text and images directly onto pi-top [4]'s OLED screen.

.. code-block:: bash

    pi-top oled display [-h] [--timeout TIMEOUT] [--font-size FONT_SIZE] text

Where:

-h, --help
     Show a help message and exits

-t, --timeout TIMEOUT
    set the timeout in seconds

--font-size FONT_SIZE
    set the font size

text
    set the text to write to screen


Example:

.. code-block:: bash

    pi@pi-top:~ $ pi-top oled display "hey!" -t 5


pi-top oled spi
~~~~~~~~~~~~~~~~~~~~~~~~~~

Control the SPI bus used by the OLED. When using `pi-top oled spi` without arguments, the SPI bus currently used by the OLED will be returned.

.. code-block:: bash

    pi-top oled spi [-h] {0,1}

Where:

-h, --help
     Show a help message and exits

{0,1}
    Optional. Set the SPI bus to be used by OLED. Valid options: 0 or 1

Example:

.. code-block:: bash

    pi@pi-top:~ $ pi-top oled spi
    1

    pi@pi-top:~ $ pi-top oled spi 0

    pi@pi-top:~ $ pi-top oled spi
    0


pi-top support
==================

Find resources to learn how to use your device and get help if needed.

.. code-block:: bash

    pi-top support


Example:

.. code-block:: bash

    pi@pi-top:~ $ pi-top support
    DOCS ==========================================
    [ ✓ ] pi-top Python SDK documentation: online version, recommended
      https://docs.pi-top.com/python-sdk/
    [ ✓ ] pi-top Python SDK documentation: offline version
      /usr/share/doc/python3-pitop/html/index.html
    OTHER ========================================
    [ ✓ ] Knowledge Base: Find answers to commonly asked questions
      https://knowledgebase.pi-top.com/
    [ ✓ ] Forum: Discuss and search through support topics.
      https://forum.pi-top.com/
