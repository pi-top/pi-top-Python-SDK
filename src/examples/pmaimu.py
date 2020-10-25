from ptpma import PMAInertialMeasurementUnit
from time import sleep

imu = PMAInertialMeasurementUnit()

choice = input(
    "Pick which sensor you would like to read: [a:Accelerometer|b:Gyrometer|c:Temperature|d:Orientation]")


# The output from the IMU is very sensitive, but for the benefit of seeing
# easier to understand numbers we formatted the output for the vectors

def print_acceleration():
    # Given as a x, y, z tuple
    print("Acceleration: {0[0]:.2f}, {0[1]:.2f}, {0[2]:.2f}".format(
        imu.acceleration))


def print_gyroscope():
    # Given as a x, y, z tuple
    print("Gyroscope: {0[0]:.2f}, {0[1]:.2f}, {0[2]:.2f}".format(imu.gyro))


def print_magnetometer():
    # Be careful keeping anything magnetic near when taking this reading
    # as it will effect the reading by a lot
    # Given as a x, y, z tuple
    print("Magnetometer: {0[0]:.2f}, {0[1]:.2f}, {0[2]:.2f}".format(
        imu.magnetic))


def print_orientation():
    # orientation is calculated using the Madgwick algorithm return as a x, y, z tuple
    print("Orientation: {0[0]:.2f}, {0[1]:.2f}, {0[2]:.2f}".format(
        imu.orientation))


def print_temperature():
    # Given in celsius
    print("Temperature: {0:.2f}".format(imu.temperature))


while True:

    if choice is "a":
        print_acceleration()
    elif choice is "b":
        print_gyroscope()
    elif choice is "c":
        print_temperature()
    elif choice is "d":
        print_orientation()
    else:
        print("Please pick valid letter")
        break

    sleep(0.1)
