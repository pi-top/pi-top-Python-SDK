from pitop import DriveController, NavigationController
from signal import pause

drive_controller = DriveController(left_motor_port="M3", right_motor_port="M0")

navigation_controller = NavigationController(drive_controller=drive_controller)

while True:
    navigation_controller.go_to(x_goal=1, y_goal=0)
    print(f"finished with state: {navigation_controller._robot_state}")

    navigation_controller.go_to(x_goal=1, y_goal=1)
    print(f"finished with state: {navigation_controller._robot_state}")

    navigation_controller.go_to(x_goal=0, y_goal=1)
    print(f"finished with state: {navigation_controller._robot_state}")

    navigation_controller.go_to(x_goal=0, y_goal=0, theta_goal=0)
    print(f"finished with state: {navigation_controller._robot_state}")

# drive_controller.robot_move(linear_speed=0, angular_speed=1)
# pause()