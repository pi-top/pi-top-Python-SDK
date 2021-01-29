=================
Overview
=================

This API provides features that are selectively available, depending on the pi-top device that you are using. To find out what is available for your pi-top device, see the relevant section below.

Choose your pi-top device to go to the relevant section:

* :ref:`pi-top [4]<overview:pi-top [4]>`
* :ref:`pi-top [3]<overview:pi-top laptops>`
* :ref:`pi-topCEED<overview:pi-topCEED>`
* :ref:`Original pi-top<overview:pi-top laptops>`

This API provides some convenience classes for :ref:`common system devices<api_system_devices:API - System Devices>`, such as:

* Camera
* Keyboard

.. * Microphone
.. * Mouse

----------------------------------------
pi-top [4]
----------------------------------------

Interacting with onboard pi-top [4] hardware
============================================

pi-top [4] supports the following API devices/components for its onboard hardware:

* :ref:`Battery<api_core:pi-top Battery>`
* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_core:pi-top [4] Miniscreen>`

pi-top [4] does not support the following API devices/components:

* :ref:`Display<api_core:pi-top Display>`

This is due to the fact that pi-top [4] has no attached display, and the pi-top [4] official display's brightness is handled in hardware with physical brightness buttons, and the backlight is handled by DPMS (the operating system's internal screen blanking functionality).

Physical computing with pi-top [4]
========================================

pi-top [4] supports the following API devices/components for physical computing:

* :ref:`pi-topPULSE (pulse)<api_pitop_peripherals:pi-topPULSE>`
* :ref:`pi-top Maker Architecture (PMA) Components<api_pma:API - pi-top Maker Architecture (PMA)  Components>`

The pi-topPULSE can be used as a Raspberry Pi HAT with a pi-top [4]. The USB camera library can be used with any USB camera, and - whilst technically can be used with any Raspberry Pi/pi-top, was designed with the pi-top [4] and PMA in mind.

pi-top [4] does not support the following API devices/components:

* :ref:`pi-topPROTO+ (protoplus)<api_pitop_peripherals:pi-topPROTO+>`

This is due to the fact that pi-topPROTO+ makes use of the legacy 'modular rail', which has no way of connecting to a pi-top [4].

Check out the :ref:`key concepts for pi-top Maker Architecture<key_concepts:pi-top Maker Architecture>` for more information.

----------------------------------------
pi-top laptops
----------------------------------------

Interacting with onboard pi-top laptop hardware
===============================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API devices/components for their onboard hardware:

* :ref:`Battery<api_core:pi-top Battery>`
* :ref:`Display<api_core:pi-top Display>`

pi-top laptops does not support the following API devices/components:

* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_core:pi-top [4] Miniscreen>`

This is due to the fact that pi-top laptops do not include the pi-top [4]'s miniscreen.

Using peripherals with a pi-top laptop
========================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API devices/components for use with peripherals:

* :ref:`pi-topPROTO+ (protoplus)<api_pitop_peripherals:pi-topPROTO+>`
* :ref:`pi-topPULSE (pulse)<api_pitop_peripherals:pi-topPULSE>`

Note that the USB camera library works with any pi-top with a USB camera connected. This was designed for pi-top [4] usage, but due to its general purpose functionality, it can technically be used if desired.

pi-topSPEAKER support is provided automagically by pt-device-manager, and so there is no exposed API for this.

pi-top laptops does not support the following API devices/components:

* :ref:`pi-top Maker Architecture (PMA) Components<api_pma:API - pi-top Maker Architecture (PMA)  Components>`

This is due to the fact that PMA is only available for pi-top [4].

----------------------------------------
pi-topCEED
----------------------------------------

Interacting with onboard pi-topCEED hardware
============================================

pi-top laptops (Original pi-top and pi-top [3]) support the following API devices/components for their onboard hardware:

* :ref:`Display<api_core:pi-top Display>`

pi-top laptops does not support the following API devices/components:

* :ref:`Battery<api_core:pi-top Battery>`
* :ref:`pi-top [4] Miniscreen - OLED and buttons (miniscreen)<api_core:pi-top [4] Miniscreen>`

This is due to the fact that pi-topCEED does not include a battery or the pi-top [4]'s miniscreen.

Using peripherals with a pi-topCEED
========================================

pi-topCEED supports the following API devices/components for use with peripherals:

* :ref:`pi-topPROTO+ (protoplus)<api_pitop_peripherals:pi-topPROTO+>`
* :ref:`pi-topPULSE (pulse)<api_pitop_peripherals:pi-topPULSE>`

Note that the USB camera library works with any pi-top with a USB camera connected. This was designed for pi-top [4] usage, but due to its general purpose functionality, it can technically be used if desired.

pi-topSPEAKER support is provided automagically by pt-device-manager, and so there is no exposed API for this.

pi-topCEED does not support the following API devices/components:

* :ref:`pi-top Maker Architecture (PMA) Components<api_pma:API - pi-top Maker Architecture (PMA)  Components>`

This is due to the fact that PMA is only available for pi-top [4].
