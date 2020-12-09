from pitop.pma import ServoMotor
from time import sleep

servo = ServoMotor("S2")
TARGET_SPEED = 25

# Scan back and forward across a 180 degree angle range in 10 degree hops

for current_angle in range(90, -100, -10):
    print("Setting angle to", current_angle)
    servo.set_target_angle_and_speed(current_angle, TARGET_SPEED)
    sleep(0.5)

for current_angle in range(-90, 100, 10):
    print("Setting angle to", current_angle)
    servo.set_target_angle_and_speed(current_angle, TARGET_SPEED)
    sleep(0.5)

sleep(1)

# Scan back and forward by setting speed only and reading current angle
STOP_ANGLE = 80

print("Setting target speed to ", -TARGET_SPEED)
servo.target_speed = -TARGET_SPEED

current_angle, current_speed = servo.current_angle_and_speed

while current_angle > -STOP_ANGLE:
    current_angle, current_speed = servo.current_angle_and_speed
    print("current_angle: {} | current_speed: {}".format(current_angle, current_speed))
    sleep(0.05)

print("Setting target speed to ", TARGET_SPEED)
servo.target_speed = TARGET_SPEED

while current_angle < STOP_ANGLE:
    current_angle, current_speed = servo.current_angle_and_speed
    print("current_angle: {} | current_speed: {}".format(current_angle, current_speed))
    sleep(0.05)
