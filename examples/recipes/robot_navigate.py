from pitop import DriveController, NavigationController

drive_controller = DriveController(left_motor_port="M3", right_motor_port="M0")

navigation_controller = NavigationController(drive_controller=drive_controller)

for _ in range(0, 2):
    navigation_controller.go_to(position=[1, 0]).wait()
    print(f"finished with state: {navigation_controller.robot_state}")

    navigation_controller.go_to(position=[1, 1]).wait()
    print(f"finished with state: {navigation_controller.robot_state}")

    navigation_controller.go_to(position=[0, 1]).wait()
    print(f"finished with state: {navigation_controller.robot_state}")

    navigation_controller.go_to(position=[0, 0], angle=0).wait()
    print(f"finished with state: {navigation_controller.robot_state}")