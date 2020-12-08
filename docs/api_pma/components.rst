
Button
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/button.jpg

A Button is a digital input device; it generates a boolean value whenever it's pressed or released.

Since it's a digital device, it should be connected to the Digital ports on the Foundation/Expansion Plates, labeled from `D0` to `D7`.


.. autoclass:: pitop.pma.Button
   :inherited-members: gpiozero.Button
   :exclude-members: pin_factory


Buzzer
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/buzzer.jpg

A Buzzer is a digital output device; it can be controlled to create an output, in this case, sound.

Since it's a digital device, it should be connected to the Digital ports on the Foundation/Expansion Plates, labeled from `D0` to `D7`.


.. autoclass:: pitop.pma.Buzzer
   :inherited-members: gpiozero.Buzzer
   :exclude-members: pin_factory


EncoderMotor
-------------------------------

A Encoder-Motor is an electromechanical device that can be controlled to move a motor's shaft to a particular position or speed.

It should be connected to the Motor ports on the Expansion Plate, labeled from `M0` to `M3`.

.. autoclass:: pitop.pma.EncoderMotor
    :exclude-members: MMK_STANDARD_GEAR_RATIO, MAX_DC_MOTOR_RPM


LED
-------------------------------

A LED is a digital output device; it can be controlled to emit light.

Since it's a digital device, it should be connected to the Digital ports on the Foundation/Expansion Plates, labeled from `D0` to `D7`.

.. image:: ../_static/pma/foundation_kit/components/led_red.jpg

.. autoclass:: pitop.pma.LED
   :inherited-members: gpiozero.LED
   :exclude-members: pin_factory


LightSensor
-------------------------------

A LightSensor is an analog input device; it measures the light at which it's exposed and generates an analog signal proportional to the amount of light.

Since it's an analog device, it should be connected to the Analog ports on the Foundation/Expansion Plates, labeled from `A0` to `A3`.

.. image:: ../_static/pma/foundation_kit/components/light_sensor.jpg

.. autoclass:: pitop.pma.LightSensor


Potentiometer
-------------------------------

A Potentiometer is an analog input device; it measures angular position and generates a proportional analog signal proportional to it.

It should be connected to the Analog ports on the Foundation/Expansion Plates, labeled from `A0` to `A3`.

.. image:: ../_static/pma/foundation_kit/components/potentiometer.jpg

.. autoclass:: pitop.pma.Potentiometer


ServoMotor
-------------------------------

A ServoMotor is an electromechanical device that can be controlled to move the angle and speed of the servo horn.

It should be connected to the ServoMotor ports on the Expansion Plate, labeled from `S0` to `S3`.

.. autoclass:: pitop.pma.ServoMotor
    :exclude-members: ANGLE_RANGE, SPEED_RANGE, MIN_PULSE_WIDTH_MICRO_S, MAX_PULSE_WIDTH_MICRO_S, REGISTER_MIN_PULSE_WIDTH, REGISTER_MAX_PULSE_WIDTH, REGISTER_PWM_FREQUENCY, PWM_FREQUENCY, PWM_PERIOD, DUTY_REGISTER_RANGE, SERVO_LOWER_DUTY, SERVO_UPPER_DUTY, RegisterTypes


SoundSensor
-------------------------------

A SoundSensor is an analog input device; it measures sound levels and generates an analog signal proportional to it.

It should be connected to the Analog ports on the Foundation/Expansion Plates, labeled from `A0` to `A3`.


.. image:: ../_static/pma/foundation_kit/components/sound_sensor.jpg

.. autoclass:: pitop.pma.SoundSensor


UltrasonicSensor
-------------------------------

A UltrasonicSensor is an analog input device; it measures distance using ultransound, generating an analog signal proportional to the measured distance.

It should be connected to the Analog ports on the Foundation/Expansion Plates, labeled from `A0` to `A3`.


.. image:: ../_static/pma/foundation_kit/components/ultrasonic_sensor.jpg

.. autoclass:: pitop.pma.UltrasonicSensor
    :exclude-members: ECHO_LOCK
