
python3-pt-buttons Reference
=============================

This library allows you to interact with the function button on the pi-top [4]. You can write code to respond to these buttons being pressed and released. The following code example shows two different ways of doing this.

To get started, copy this code into your program and see what you can make using the buttons.

Note: when you write a program that interacts with the pi-top [4] buttons, you will not be able to use them to control the mini-screen system menu.


.. literalinclude:: ../examples/case_buttons/buttons_example.py



PTButton
====================

.. autoclass:: pitop.case_buttons.PTButton
    :members:

    .. automethod:: __init__

PTButtons
====================

.. autoclass:: pitop.case_buttons.PTButtons

PTUpButton
====================

.. autofunction:: pitop.case_buttons.PTUpButton

PTDownButton
====================

.. autofunction:: pitop.case_buttons.PTDownButton

PTSelectButton
====================

.. autofunction:: pitop.case_buttons.PTSelectButton

PTCancelButton
====================

.. autofunction:: pitop.case_buttons.PTCancelButton
