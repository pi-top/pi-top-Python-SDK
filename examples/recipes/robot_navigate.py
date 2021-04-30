from pitop import DriveController, NavigationController, IMU
from pitop.pma import UltrasonicSensor
from time import sleep
import numpy as np


def navigation_finished():
    global goal_reached
    goal_reached = True
    print(f"Goal reached with state: \n{navigate.robot_state}")


def check_for_obstacles():
    while not goal_reached:
        sleep(0.15)
        if ultrasonic.distance < 0.25:
            print("Obstacle blocking navigation goal, changing to next goal!")
            navigate.stop()
            sleep(1)
            break


def set_goal_with_obstacle_detection(position, angle=None):
    global goal_reached
    goal_reached = False
    navigate.go_to(position=position, angle=angle, on_finish=navigation_finished).wait()
    # check_for_obstacles()


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
    navigate.go_to(position=(0, 0), angle=0, on_finish=navigation_finished, backwards=True).wait()
    # navigate.robot_state._saver.to_array()
    # x = navigate.robot_state._saver.x
    # x_prior = navigate.robot_state._saver.x_prior
    # P_prior = navigate.robot_state._saver.P_prior
    # P = navigate.robot_state._saver.P
    # z = navigate.robot_state._saver.z
    # y = navigate.robot_state._saver.y
    #
    # with open(r"nav_data.npy", "wb") as f:
    #     np.save(f, x)
    #     np.save(f, x_prior)
    #     np.save(f, P_prior)
    #     np.save(f, P)
    #     np.save(f, z)
    #     np.save(f, y)

    # with open(r"nav_data_x.pickle", "wb") as output_file:
    #     pickle.dump(x, output_file)
    #
    # with open(r"nav_data_x.pickle", "wb") as output_file:
    #     pickle.dump(x, output_file)


goal_reached = False
navigate = NavigationController(
    drive_controller=DriveController(left_motor_port="M3", right_motor_port="M0"),
    imu=IMU()
)
# ultrasonic = UltrasonicSensor("D3")

main()
