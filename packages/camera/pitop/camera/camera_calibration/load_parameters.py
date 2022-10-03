import os
import pickle

# directory where calibration output pickle file is located
calibration_outputs_dir = ""
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, calibration_outputs_dir)

# Filename used to save the camera calibration result (mtx, dist)
calibration_mtx_dist_filename = "camera_cal_dist_pickle_640-480.p"

# Camera resolution used for calibration
calibration_width = 640
calibration_height = 480


def load_camera_cal(width: int, height: int):
    """Read in the saved camera matrix and distortion coefficients These are
    the arrays we calculated using cv2.calibrateCamera() Also scales
    calibration matrix based on resolution being used."""

    dist_pickle = pickle.load(
        open(os.path.join(abs_file_path, calibration_mtx_dist_filename), "rb")
    )

    mtx = dist_pickle["mtx"]
    dist = dist_pickle["dist"]

    scale_factor_x = width / calibration_width
    scale_factor_y = height / calibration_height

    mtx[0][0] = mtx[0][0] * scale_factor_x
    mtx[1][1] = mtx[1][1] * scale_factor_y
    mtx[0][2] = mtx[0][2] * scale_factor_x
    mtx[1][2] = mtx[1][2] * scale_factor_y

    return mtx, dist
