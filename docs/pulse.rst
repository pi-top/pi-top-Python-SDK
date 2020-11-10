======================================================
pi-topPULSE
======================================================

pi-topPULSE EEPROM
------------------------------------------------------

The pi-topPULSE contains an EEPROM which was programmed using the
settings file contains in this directory. See the Raspberry Pi
Foundation's `HAT Github
repository <https://github.com/raspberrypi/hats>`__ for more
information.


Manually Configuring Raspbian for pi-topPULSE
------------------------------------------------------

**Note:** This document was moved here from the Github project wiki.
**Note:** This is definitely the long way round to get the pi-topPULSE
working, and is provided only for interest. If you are running pi-topOS,
you do not need to worry about this - everything is already included! If
you are running Raspbian, please consult the ``readme.md`` file
`here <https://github.com/pi-top/pi-topPULSE/blob/master/README.md>`__
for the simpler method of enabling the pulse.

Enabling I2C
~~~~~~~~~~~~

I2C is required to communicate with the function-enabling IC as part of
initialisation.

The simplest way to do this is by running ``raspi-config``, selecting
``Interfacing Options`` → ``I2C`` → Select "Yes" to enabling I2C.

Enabling UART/serial for LEDs and Microphone
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The included version of Pyserial on Raspbian on Python 3 does not
support custom baud rates, which is required for LEDs to work. Run the
``upgrade-python3-pyserial`` script in the
`manual-install </manual-install/@master>`__ folder to update to the
latest version of Pyserial.

You will also need to enable UART. The simplest way to do this is by
running ``raspi-config``, selecting ``Interfacing Options`` → ``Serial``
→ Select "No" to enabling a login shell accessible over serial → Select
"Yes" for enabling serial port hardware.

Configuring Audio Output (Speaker)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enabling HDMI to I2S on the pi-top v2
'''''''''''''''''''''''''''''''''''''

The new pi-top has built-in HDMI-to-I2S audio conversion, which
eliminates the need for reconfiguring the operating system to use I2S.
Enabling this requires communicating with the hub, which can be as
follows:

::

   sudo apt install python3-pt-common

Now you can use
`pt-hdmi-to-i2s <https://github.com/pi-top/pi-topHUB-v2/blob/master/manual-install/pt-hdmi-to-i2s>`__
as follows:

::

   pt-hdmi-to-i2s enable
   pt-hdmi-to-i2s disable

Configuring I2S on the original pi-top (v1) and pi-topCEED
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

I2S enabling/disabling and volume control configuration on the original
pi-top (v1) and pi-topCEED form part of the `general pi-top device
management system <https://github.com/pi-top/Device-Management>`__,
however can be configured manually via the following commands, followed
by a reboot, using
`pt-i2s <https://github.com/pi-top/Device-Management/blob/master/src/i2s/pt-i2s>`__:

::

   pt-i2s enable
   pt-i2s disable

Volume control for pi-topPULSE can be enabled by loading soundcard
device information with the following command (with a pi-topPULSE
connected, and with I2S enabled), followed by a reboot, using
`hifiberry-alsactl.restore <https://github.com/pi-top/Device-Management/blob/master/src/i2s/hifiberry-alsactl.restore>`__:

::

   /usr/sbin/alsactl -f hifiberry-alsactl.restore restore

Making the ``ptpulse`` Python library accessible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to get the pi-topPULSE library is to install the debian
package directly:

::

   sudo apt install python3-pt-pulse

You can also download the library files from this repository and use
them locally.

Using the software library to manually initialise pi-topPULSE
-------------------------------------------------------------

Once you have installed the library, you can now initialise the device:

::

   from ptpulse import configuration as ptpulsecfg

   host_device_id = 2
   ptpulsecfg.initialise(host_device_id)
   enabled, reboot_required, v2_hub_hdmi_to_i2s_required = ptpulsecfg.enable_device()

   if (reboot_required):
       print("Reboot required")
   elif (v2_hub_hdmi_to_i2s_required):
       print("HDMI to I2S required")
   elif (enabled):
       print("Successfully enabled pi-topPULSE")
   else:
       print("Failed to enable pi-topPULSE")

\*\* NOTE: the host device ID for your device can be found
`here <https://github.com/pi-top/Device-Management/blob/master/library/pitop.utils/common_ids.py>`__\ \*\*

Using pi-topPULSE in projects
-----------------------------

You are now ready to use the pi-topPULSE! Check out the examples to get some inspiration of how
you can use it.
