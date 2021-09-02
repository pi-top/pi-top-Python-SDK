from time import sleep

from pitop import BrakingType, EncoderMotor, ForwardDirection

# Setup the motor

motor = EncoderMotor("M0", ForwardDirection.COUNTER_CLOCKWISE)
motor.braking_type = BrakingType.COAST


# Move in both directions

rpm_speed = 100
for _ in range(4):
    motor.set_target_rpm(rpm_speed)
    sleep(2)
    motor.set_target_rpm(-rpm_speed)
    sleep(2)

motor.stop()
