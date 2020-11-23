==========================
Frequently Asked Questions
==========================

-----------------------
How does this SDK work?
-----------------------

------------
What is PMA?
------------

--------------------------------------------------
I keep getting an Exception - what is the problem?
--------------------------------------------------

-----------------------------
Where did this SDK come from?
-----------------------------
Note: epoch version

---------------------------------------------------------------------------------------
I was using an older version of the Python libraries. How can I update to use this SDK?
---------------------------------------------------------------------------------------
Note: .deprecated directory.
PMA: PMA prefix is now dropped
Buttons: PT prefix is now dropped. 'Buttons' is now 'CaseButtons'

Everything else should be updatable with a Find and Replace:

ptbuttons -> pitop.miniscreen.buttons
ptoled -> pitop.miniscreen.oled
ptpma -> pitop.pma
ptpulse -> pitop.pulse
ptprotoplus -> pitop.protoplus

.. _faq-lost-oled-menu:
----------------------------------
I lost my OLED menu - where is it?
----------------------------------
When a program 'takes control' of the OLED, the OLED will clear itself of the `pt-sys-oled`
menu, and is then controlled by your code. You will not be able to access the system menu on the mini-screen
until your program exits, at which point the system menu is automatically restored.

In a similar way, when a program 'takes control' of the mini-screen buttons, they can no longer be used to
navigate the menu.

If you need to provide yourself with a method of being able to exit, it is recommended that you check for a
press event on the 'cancel' button:

.. literalinclude:: ../../examples/miniscreen/exit_with_cancel_button.py
