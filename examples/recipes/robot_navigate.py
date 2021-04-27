from pitop import DriveController, NavigationController
from pitop.pma import UltrasonicSensor
from time import sleep


def navigation_finished():
    global goal_reached
    goal_reached = True
    print(f"Goal reached with state: \n{navigation_controller.robot_state}")


def check_for_obstacles():
    while not goal_reached:
        sleep(0.15)
        if ultrasonic.distance < 0.25:
            print("Obstacle blocking navigation goal, changing to next goal!")
            navigation_controller.stop()
            sleep(1)
            break


def set_goal_with_obstacle_detection(position, angle=None):
    global goal_reached
    goal_reached = False
    navigation_controller.go_to(position=position, angle=angle, on_finish=navigation_finished)
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
    navigation_controller.go_to(position=(0, 0), angle=0, on_finish=navigation_finished, backwards=True).wait()


goal_reached = False
navigation_controller = NavigationController(
    drive_controller=DriveController(left_motor_port="M3", right_motor_port="M0")
)
ultrasonic = UltrasonicSensor("D3")

main()
