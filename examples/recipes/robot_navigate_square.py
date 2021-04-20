from pitop import DriveController, NavigationController

drive_controller = DriveController(left_motor_port="M3", right_motor_port="M0")

navigation_controller = NavigationController(drive_controller=drive_controller)

while True:
    navigation_controller.go_to()
