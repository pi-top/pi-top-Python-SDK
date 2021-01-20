from pitop.pma import EncoderMotor, ForwardDirection, BrakingType
from threading import Thread
from time import sleep

# Setup the motors for the rover configuration

motor_left = EncoderMotor("M3", ForwardDirection.CLOCKWISE)
motor_right = EncoderMotor("M0", ForwardDirection.COUNTER_CLOCKWISE)

motor_left.braking_type = BrakingType.COAST
motor_right.braking_type = BrakingType.COAST


# Define some functions for easily controlling the rover

def drive(target_rpm: float):

    print("Start driving at target", target_rpm, "rpm...")
    motor_left.set_target_rpm(target_rpm)
    motor_right.set_target_rpm(target_rpm)


def stop_rover():

    print("Stopping rover...")
    motor_left.stop()
    motor_right.stop()


def turn_left(rotation_speed: float):

    print("Turning left...")
    motor_left.stop()
    motor_right.set_target_rpm(rotation_speed)


def turn_right(rotation_speed: float):

    print("Turning right...")
    motor_right.stop()
    motor_left.set_target_rpm(rotation_speed)

# Start a thread to monitor the rover


def monitor_rover():
    while True:
        print("> Rover motor RPM's (L,R):", round(motor_left.current_rpm, 2), round(motor_right.current_rpm, 2))
        sleep(1)


monitor_thread = Thread(target=monitor_rover, daemon=True)
monitor_thread.start()

# Go!

rpm_speed = 100
for _ in range(4):

    drive(rpm_speed)
    sleep(5)

    turn_left(rpm_speed)
    sleep(5)

stop_rover()
