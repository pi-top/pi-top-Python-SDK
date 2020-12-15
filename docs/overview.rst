.. TODO: link to API page for each section

.. * :ref:`Battery<API - Battery>`.
.. * :ref:`Display<API - Display>`.
.. * :ref:`pi-topPROTO+ (protoplus)<API - pi-topPROTO+>`.
.. * :ref:`System<API - System>`.

=================
Overview
=================

This API provides features that are selectively available, depending on the pi-top device that you are using. To find out what is available for your pi-top device, see the relevant section below.

Choose your pi-top device to go to the relevant section:

* :ref:`pi-top [4]<overview:pi-top [4]>`
* :ref:`pi-top [3]<overview:pi-top laptops>`
* :ref:`pi-topCEED<overview:pi-topCEED>`
* :ref:`Original pi-top<overview:pi-top laptops>`

----------------------------------------
pi-top [4]
----------------------------------------

Interacting with onboard pi-top [4] hardware
============================================

pi-top [4] supports the following API sections for its onboard hardware:

* Battery
* :ref:`USB Camera (camera)<api_camera:API - pi-top Camera Input Component>`
* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_miniscreen:API - pi-top [4] Miniscreen>`
* :ref:`pi-top Maker Architecture (pma)<api_pma:API - pi-top Makers Architecture (PMA)>`
* :ref:`pi-topPULSE (pulse)<api_pulse:API - pi-topPULSE>`
* System

pi-top [4] does not support the following API sections:

* Display
* pi-topPROTO+

This is due to the fact that pi-top [4] has no attached display, and the pi-top [4] official display's brightness is handled in hardware with physical brightness buttons, and the backlight is handled by DPMS (the operating system's internal screen blanking functionality).

Physical computing with pi-top [4]
========================================

pi-top [4] supports the following API sections for physical computing:

* :ref:`USB Camera (camera)<api_camera:API - pi-top Camera Input Component>`
* :ref:`pi-top Maker Architecture (pma)<api_pma:API - pi-top Makers Architecture (PMA)>`

See :ref:`getting_started_pma:Getting Started with pi-top Maker Architecture`

----------------------------------------
pi-top laptops
----------------------------------------

Interacting with onboard pi-top laptop hardware
===============================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API sections for their onboard hardware:

* Battery
* Display
* System

pi-top laptops does not support the following API sections:

* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_miniscreen:API - pi-top [4] Miniscreen>`

This is due to the fact that pi-top laptops do not include the pi-top [4]'s miniscreen.

Using peripherals with a pi-top laptop
========================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API sections for use with peripherals:

* pi-topPROTO+
* :ref:`pi-topPULSE (pulse)<api_pulse:API - pi-topPULSE>`
* :ref:`USB Camera (camera)<api_camera:API - pi-top Camera Input Component>`

Note that the USB camera library works with any pi-top with a USB camera connected. This was designed for pi-top [4] usage, but due to its general purpose functionality, it can technically be used if desired.

pi-topSPEAKER support is provided automagically by pt-device-manager, and so there is no exposed API for this.

pi-top laptops does not support the following API sections:

* :ref:`pi-top Maker Architecture (pma)<api_pma:API - pi-top Makers Architecture (PMA)>`

This is due to the fact that pi-top laptops do not support PMA.

----------------------------------------
pi-topCEED
----------------------------------------

Interacting with onboard pi-topCEED hardware
============================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API sections for their onboard hardware:

* Display
* System

pi-top laptops does not support the following API sections:

* Battery
* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_miniscreen:API - pi-top [4] Miniscreen>`

This is due to the fact that pi-topCEED does not include a battery or the pi-top [4]'s miniscreen.

Using peripherals with a pi-topCEED
========================================

pi-topCEED supports the following API sections for use with peripherals:

* pi-topPROTO+
* :ref:`pi-topPULSE (pulse)<api_pulse:API - pi-topPULSE>`
* :ref:`USB Camera (camera)<api_camera:API - pi-top Camera Input Component>`

Note that the USB camera library works with any pi-top with a USB camera connected. This was designed for pi-top [4] usage, but due to its general purpose functionality, it can technically be used if desired.

pi-topSPEAKER support is provided automagically by pt-device-manager, and so there is no exposed API for this.

pi-topCEED does not support the following API sections:

* :ref:`pi-top Maker Architecture (pma)<api_pma:API - pi-top Makers Architecture (PMA)>`

This is due to the fact that pi-topCEED do not support PMA.

----------------------------------------
Making use of additional helper classes
----------------------------------------

TODO: determine additional helpers - keyboard, speech, etc.
