=======================================================================
pi-top Keyboard Input Component
=======================================================================

This module has been designed to allow a programmer to utilise keyboard input in the same way as
they might use GPIO input (e.g. a button).

You can listen for any standard keyboard key input, for example by using ``a`` or ``A`` to listen
for the A-key being pressed with or without shift.

KeyPressListener
----------------------

**Example Code:**

.. literalinclude:: ../../examples/keyboard/keyboard.py

.. autoclass:: pitop.keyboard.KeyPressListener


Special Key Names
#####################

You can listen for the following special keys by passing their names when creating an instance
of KeyPressListener.

==================      ============
Identifier              Description
==================      ============
``alt``                 A generic Alt key. This is a modifier.
``alt_l``               The left Alt key. This is a modifier.
``alt_r``               The right Alt key. This is a modifier.
``alt_gr``              The AltGr key. This is a modifier.
``backspace``           The Backspace key.
``caps_lock``           The CapsLock key.
``cmd``                 A generic command button.
``cmd_l``               The left command button. On PC keyboards, this corresponds to the
                        Super key or Windows key, and on Mac keyboards it corresponds to the Command
                        key. This may be a modifier.
``cmd_r``               The right command button. On PC keyboards, this corresponds to the
                        Super key or Windows key, and on Mac keyboards it corresponds to the Command
                        key. This may be a modifier.
``ctrl``                A generic Ctrl key. This is a modifier.
``ctrl_l``              The left Ctrl key. This is a modifier.
``ctrl_r``              The right Ctrl key. This is a modifier.
``delete``              The Delete key.
``down``                A down arrow key.
``up``                  An up arrow key.
``left``                A left arrow key.
``right``               A right arrow key.
``end``                 The End key.
``enter``               The Enter or Return key.
``esc``                 The Esc key.
``home``                The Home key.
``page_down``           The PageDown key.
``page_up``             The PageUp key.
``shift``               A generic Shift key. This is a modifier.
``shift_l``             The left Shift key. This is a modifier.
``shift_r``             The right Shift key. This is a modifier.
``space``               The Space key.
``tab``                 The Tab key.
``insert``              The Insert key. This may be undefined for some platforms.
``menu``                The Menu key. This may be undefined for some platforms.
``num_lock``            The NumLock key. This may be undefined for some platforms.
``pause``               The Pause/Break key. This may be undefined for some platforms.
``print_screen``        The PrintScreen key. This may be undefined for some platforms.
``scroll_lock``         The ScrollLock key. This may be undefined for some platforms.
``f1``                  The F1 key
``f2``                  The F2 key
``f3``                  The F3 key
``f4``                  The F4 key
``f5``                  The F5 key
``f6``                  The F6 key
``f7``                  The F7 key
``f8``                  The F8 key
``f9``                  The F9 key
``f10``                 The F10 key
``f11``                 The F11 key
``f12``                 The F12 key
``f13``                 The F13 key
``f14``                 The F14 key
``f15``                 The F15 key
``f16``                 The F16 key
``f17``                 The F17 key
``f18``                 The F18 key
``f19``                 The F19 key
``f20``                 The F20 key
==================      ============
