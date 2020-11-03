from pitop.pma import ServoMotor
from time import sleep

servo = ServoMotor("S2")

# Scan back and forward across a 180 degree angle range in 10 degree hops

for angle in range(90, -100, -10):
    sleep(1)
    print("Setting angle to", angle)
    servo.set_target_angle(angle, 10)

for angle in range(-90, 100, 10):
    sleep(1)
    print("Setting angle to", angle)
    servo.set_target_angle(angle, 10)

sleep(1)

# Scan back and forward by setting the speed and waiting

speed = 10

print("Setting target speed to ", -speed)
servo.set_target_speed(-speed)
sleep(5)

print("Setting target speed to ", speed)
servo.set_target_speed(speed)
sleep(5)
