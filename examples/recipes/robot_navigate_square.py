"""Demo of how to use the Navigation Controller to control a robot. Place your.

robot (preferably the Alex or Bobbie configuration) in the middle of a 1x1 meter square and run the code - the robot
will drive around the square twice and then back to the middle. The Ultrasonic Sensor is also used to detect obstacles
during navigation. If one is found, the robot will move onto the next navigation goal.
"""

from time import sleep

from pitop import NavigationController, Pitop
from pitop.pma import UltrasonicSensor


def navigation_finished():
    global goal_reached
    goal_reached = True
    print(f"Goal reached with state: \n{robot.navigate.state_tracker}")


def check_for_obstacles():
    while not goal_reached:
        sleep(0.15)
        if robot.ultrasonic.distance < 0.2:
            print("Obstacle blocking navigation goal, changing to next goal!")
            robot.navigate.stop()
            sleep(1)
            break


def set_goal_with_obstacle_detection(position, angle=None):
    global goal_reached
    goal_reached = False
    robot.navigate.go_to(position=position, angle=angle, on_finish=navigation_finished)
    check_for_obstacles()


def main():
    square_side_length = 1.0  # m
    square_top_right = (square_side_length / 2, -square_side_length / 2)
    square_top_left = (square_side_length / 2, square_side_length / 2)
    square_bottom_left = (-square_side_length / 2, square_side_length / 2)
    square_bottom_right = (-square_side_length / 2, -square_side_length / 2)

    for _ in range(0, 2):
        set_goal_with_obstacle_detection(position=square_top_right)
        set_goal_with_obstacle_detection(position=square_top_left)
        set_goal_with_obstacle_detection(position=square_bottom_left)
        set_goal_with_obstacle_detection(position=square_bottom_right)

    # go back to start_position
    robot.navigate.go_to(
        position=(0, 0), angle=0, on_finish=navigation_finished, backwards=True
    ).wait()
    print(f"Goal reached with state: \n{robot.navigate.state_tracker}")


goal_reached = False
robot = Pitop()
robot.add_component(NavigationController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(UltrasonicSensor("D3"))

main()
