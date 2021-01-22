from pitop import AlexRobot

from time import sleep


# Setup robot
robot = AlexRobot(
    motor_left_port="M3",
    motor_right_port="M0",
    ultrasonic_sensor_port="D1")

# Move it
robot.forward(0.5)
sleep(2)
robot.left(0.5)
sleep(2)
robot.backward(0.5)
sleep(2)
robot.right(0.5)
sleep(2)
