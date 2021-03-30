import pickle
import os

# directory where calibration output pickle file is located
calibration_outputs_dir = 'calibration_output'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, calibration_outputs_dir)

# Filename used to save the camera calibration result (mtx,dist)
calibration_mtx_dist_filename = 'camera_cal_dist_pickle.p'


def load_camera_cal():
    """
    Read in the saved camera matrix and distortion coefficients
    These are the arrays we calculated using cv2.calibrateCamera()
    """

    dist_pickle = pickle.load(open(os.path.join(abs_file_path, calibration_mtx_dist_filename), "rb"))
    mtx = dist_pickle["mtx"]
    dist = dist_pickle["dist"]

    return mtx, dist
