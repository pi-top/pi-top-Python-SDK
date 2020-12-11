from pitop.pma.common import ImuCalibration
import numpy as np

imu_cal = ImuCalibration()
with open('/home/pi/test_data.npy', 'rb') as f:
    mag_data = np.load(f)
# imu_cal.calibrate_magnetometer(save_data_name="/home/pi/test_data.npy")
imu_cal.calibrate_magnetometer(mag_data, update_mcu=False)
imu_cal.plot_graphs()
