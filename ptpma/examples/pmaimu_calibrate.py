from ptpma import PMAInertialMeasurementUnit

imu = PMAInertialMeasurementUnit()

# Calibrating the imu sensor will give you more accurate readings
# Note that for majority of users you will only need to do this once
# Run this script and follow the on screen instructions
imu.calibrate()
