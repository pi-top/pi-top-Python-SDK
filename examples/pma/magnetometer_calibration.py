from pitop.pma.common import ImuCalibration
import numpy as np

imu_cal = ImuCalibration()
with open('/home/pi/test_data.npy', 'rb') as f:
    mag_data = np.load(f)
# hard_iron_offset, soft_iron_matrix = imu_cal.calibrate_magnetometer(save_data_name="/home/pi/test_data.npy")
hard_iron_offset, soft_iron_matrix = imu_cal.calibrate_magnetometer()
print("hard_iron_offset: \n{}".format(hard_iron_offset))
print("soft_iron_matrix: \n{}".format(soft_iron_matrix))
imu_cal.plot_graphs()
