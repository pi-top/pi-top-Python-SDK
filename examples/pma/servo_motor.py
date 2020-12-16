from pitop.pma import ServoMotor, ServoMotorState
from time import sleep

servo = ServoMotor("S0")

# Scan back and forward across a 180 degree angle range in 10 degree hops using default servo speed
for angle in range(90, -100, -10):
    print("Setting angle to", angle)
    servo.target_angle = angle
    sleep(0.5)

for angle in range(-90, 100, 10):
    print("Setting angle to", angle)
    servo.target_angle = angle
    sleep(0.5)

sleep(1)

# Scan back and forward by setting speed only and reading current angle
STOP_ANGLE = 80
TARGET_SPEED = 25

print("Setting target speed to ", -TARGET_SPEED)
servo.target_speed = -TARGET_SPEED

current_state = servo.state
current_angle = current_state.angle

while current_angle > -STOP_ANGLE:
    current_state = servo.state
    current_angle = current_state.angle
    current_speed = current_state.speed
    print("current_angle: {} | current_speed: {}".format(current_angle, current_speed))
    sleep(0.05)

print("Setting target speed to ", TARGET_SPEED)
servo.target_speed = TARGET_SPEED

while current_angle < STOP_ANGLE:
    current_state = servo.state
    current_angle = current_state.angle
    current_speed = current_state.speed
    print("current_angle: {} | current_speed: {}".format(current_angle, current_speed))
    sleep(0.05)
