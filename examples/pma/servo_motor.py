from pitop import ServoMotor, ServoMotorSetting
from time import sleep

servo = ServoMotor("S0")

# Scan back and forward across a 180 degree angle range in 30 degree hops using default servo speed
for angle in range(90, -100, -30):
    print("Setting angle to", angle)
    servo.target_angle = angle
    sleep(0.5)

# you can also set angle with a different speed than the default
servo_settings = ServoMotorSetting()
servo_settings.speed = 25

for angle in range(-90, 100, 30):
    print("Setting angle to", angle)
    servo_settings.angle = angle
    servo.setting = servo_settings
    sleep(0.5)

sleep(1)

# Scan back and forward displaying current angle and speed
STOP_ANGLE = 80
TARGET_SPEED = 40

print("Sweeping using speed ", -TARGET_SPEED)
servo.target_speed = -TARGET_SPEED

current_state = servo.setting
current_angle = current_state.angle

# sweep using the already set servo speed
servo.sweep()
while current_angle > -STOP_ANGLE:
    current_state = servo.setting
    current_angle = current_state.angle
    current_speed = current_state.speed
    print(f"current_angle: {current_angle} | current_speed: {current_speed}")
    sleep(0.05)

print("Sweeping using speed ", TARGET_SPEED)

# you can also sweep specifying the speed when calling the sweep method
servo.sweep(speed=TARGET_SPEED)
while current_angle < STOP_ANGLE:
    current_state = servo.setting
    current_angle = current_state.angle
    current_speed = current_state.speed
    print(f"current_angle: {current_angle} | current_speed: {current_speed}")
    sleep(0.05)
