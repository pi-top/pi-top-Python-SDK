from time import sleep
import pygame
import random
from datetime import datetime
from pitop import ServoMotor, ServoMotorSetting, UltrasonicSensor, LED, LightSensor, Button

sfx_index = tuple((
    [0.5,2.9],
    [6,2.8],
    [11.4,1.2],
    [15,1.2],
    [18.8,2.5],
    [23.5,2.4],
    [28,2.1],
    [32.6,2.2],
    [37.5,2.3],
    [41.1,1.8],
    [44.6,2.3],
    [48.3,2.3],
    [52,2.3],
    [55.7,2.7],
    [61,3.5],
    [66.7,3.6],
    [72.7,4.3],
    [78.2,4.3],
    [85.5,4],
    [93.2,3.6],
    [98.5,6.8],
    [107.5,13.1],
    [125.8,4.1],
    [133.3,8.5],
    [143,8.4],
    [154.5,3.1],
    [160,3.3],
    [165.5,1.9],
    [169.3,2],
    [172.9,1.2],
    [177.5,1.4],
    [182.1,1.5],
    [186.7,1.5],
    [191.3,1],
    [195,1.3],
    [198.7,1.7],
    [202.4,1.8],
    [206,1],
    [209.7,1]
))

print(datetime.now())
distance_sensor = UltrasonicSensor("A1", threshold_distance=0.3)
left_eye = LED("D3")
right_eye = LED("D4")
mouth1 = LED("D2")
mouth2 = LED("D5")
light_sensor = LightSensor("A2")
button = Button("D0")

pygame.mixer.init()
pygame.mixer.music.set_volume(1)  # quiet for testing late at night

def resting_position():
    # Set arms to resting position
    right_arm = ServoMotor("S0")
    right_arm_servo_settings = ServoMotorSetting()
    right_arm_servo_settings.speed = 200
    right_arm_servo_settings.angle = -20
    right_arm.setting = right_arm_servo_settings
    left_arm = ServoMotor("S3")
    left_arm_servo_settings = ServoMotorSetting()
    left_arm_servo_settings.speed = 200
    left_arm_servo_settings.angle = 20
    left_arm.setting = left_arm_servo_settings


def dinner_time():
    mouth1.on()
    mouth2.on()
    #pygame.mixer.init()
    pygame.mixer.music.load("cookie.ogg")
    #pygame.mixer.music.set_volume(0.1) #quiet for testing late at night
    #pygame.mixer.music.play()
    #while pygame.mixer.music.get_busy():
    #    continue
    right_arm = ServoMotor("S0")
    right_arm_servo_settings = ServoMotorSetting()
    right_arm_servo_settings.speed = 200
    right_arm.target_angle = -15
    left_arm = ServoMotor("S3")
    left_arm_servo_settings = ServoMotorSetting()
    left_arm_servo_settings.speed = 200
    left_arm.target_angle = 15
    #sleep(3)
    pygame.mixer.music.play()
    #servo.target_angle = -70
    left_arm_servo_settings.angle = -70
    left_arm.setting = left_arm_servo_settings
    sleep(0.5)
    right_arm_servo_settings.angle = 70
    right_arm.setting = right_arm_servo_settings
    sleep(0.5)
    resting_position()
    #sleep(5)
    for chomps in range(0, 8, 1):
        #right_arm_servo_settings.angle = 0
        left_arm_servo_settings.angle = 0
        #right_arm.setting = right_arm_servo_settings
        left_arm.setting = left_arm_servo_settings
        sleep(0.25)
        #right_arm_servo_settings.angle = -15
        left_arm_servo_settings.angle = 15
        #right_arm.setting = right_arm_servo_settings
        left_arm.setting = left_arm_servo_settings
        sleep(0.25)
    sleep(0.5)
    right_arm_servo_settings.angle = 0
    left_arm_servo_settings.angle = 0
    right_arm.setting = right_arm_servo_settings
    left_arm.setting = left_arm_servo_settings
    sleep(0.25)
    right_arm_servo_settings.angle = -15
    left_arm_servo_settings.angle = 15
    right_arm.setting = right_arm_servo_settings
    left_arm.setting = left_arm_servo_settings
    sleep(0.25)
    mouth1.off()
    mouth2.off()

def head_pats():
    pygame.mixer.music.load("growling.ogg")
    random.seed(datetime.now()) #make the RNG suck less
    random_index = random.randint(0, len(sfx_index) - 1) #determine which SFX we're going to play within the track
    #print("Playing SFX #" + random_index + "    Start time: " + sfx_index[random_index][0] + "   Duration: " + sfx_index[random_index][1])
    print("Playing SFX #%3d    Start time: %5.2f   Duration: %5.2f" % (random_index,sfx_index[random_index][0],sfx_index[random_index][1]))
    pygame.mixer.music.play(start=sfx_index[random_index][0])
    mouth1.on()
    mouth2.on()
    sleep(sfx_index[random_index][1])
    pygame.mixer.music.stop()
    mouth1.off()
    mouth2.off()
    #while pygame.mixer.music.get_busy():
    #    sleep(0.1) #wait for sound to finish
    print("Playback finished")

#Main
resting_position()
while True:
    #sleep(0.1)
    if light_sensor.reading < 25:
        left_eye.on()
        right_eye.on()
    else:
        left_eye.off()
        right_eye.off()
    #print(distance_sensor.distance)
    if distance_sensor.distance < 0.2:
        head_pats()
    if button.is_pressed is True:
        dinner_time()
        resting_position()


# Set up functions to print when an object crosses 'threshold_distance'
#distance_sensor.when_in_range = dinner_time() #lambda: print("in range")
#distance_sensor.when_out_of_range = lambda: print("out of range")

#while True:
    # Print the distance (in meters) to an object in front of the sensor
 #   print(distance_sensor.distance)
  #  sleep(0.1)



#servo.target_angle = 90
#sleep(5)

exit()












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
