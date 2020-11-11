=================================================
API - Output Components
=================================================

These output device component interfaces have been provided for simple use of everyday components, and are intended for general use with the devices they represent.

These components are considered outputs due to their ability to be controlled.


Digital Components (D Port)
=================================================

Buzzer
-------------------------------

.. autoclass:: pitop.pma.Buzzer
   :inherited-members: gpiozero.Buzzer
   :exclude-members: pin_factory

LED
-------------------------------

.. autoclass:: pitop.pma.LED
   :inherited-members: gpiozero.LED
   :exclude-members: pin_factory


Encoder Motor (M Port)
=================================================

EncoderMotor
-------------------------------

.. autoclass:: pitop.pma.EncoderMotor
    :exclude-members: MMK_STANDARD_GEAR_RATIO, MAX_DC_MOTOR_RPM

Servo Motor (S Port)
=================================================

ServoMotor
-------------------------------

.. autoclass:: pitop.pma.ServoMotor
    :exclude-members: ANGLE_RANGE, SPEED_RANGE, MIN_PULSE_WIDTH_MICRO_S, MAX_PULSE_WIDTH_MICRO_S, REGISTER_MIN_PULSE_WIDTH, REGISTER_MAX_PULSE_WIDTH, REGISTER_PWM_FREQUENCY, PWM_FREQUENCY, PWM_PERIOD, DUTY_REGISTER_RANGE, SERVO_LOWER_DUTY, SERVO_UPPER_DUTY, RegisterTypes
