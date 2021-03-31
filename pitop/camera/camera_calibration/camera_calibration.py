import numpy as np
import cv2
import glob
import pickle
from os.path import join, basename
from pitop.miniscreen.buttons import SelectButton
from pitop import Camera
from time import sleep
import sys

# Where are the camera images for calibration?
camera_cal_dir_glob = 'calibration_images/calibration*.jpg'

# Where you want to save the calibration outputs?
calibration_outputs_dir = 'calibration_output'

# Filename to save the camera calibration result for later use (mtx, dist)
calibration_mtx_dist_filename = 'camera_cal_dist_pickle_640-480-2.p'

# Chessboard numbers of internal corners (nx,ny)
chessboard_size = (8, 6)
square_size = 0.025  # 25 mm squares


def get_images():
    print("Use the circle button on pi-top [4] to take 12 photos for the camera calibration process.")
    print("Use as many different perspectives as you can and try to vary the distance a little too.")
    frame_id = 0
    select_button = SelectButton()
    camera = Camera(resolution=(640, 480), format="OpenCV")

    while frame_id < 12:
        frame = camera.get_frame()
        # frame = cv2.flip(frame, 1)
        cv2.imshow('frame', frame)  # display the captured image
        if select_button.is_pressed:
            cv2.imwrite('calibration_images/calibration{}.jpg'.format(frame_id), frame)
            print("Frame written to file with ID: {}\n".format(frame_id))
            frame_id += 1
            sleep(0.5)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def calibrate_camera_and_pickle_mtx_dist():
    '''
    Calibrate camera based on set of chessboard images.
    Undistort one of the images from camera set as a test.
    Save the camera calibration results for later use (mtx,dst)
    '''
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    print("Starting calibration process...")

    # Make a list of calibration images
    images = glob.glob(camera_cal_dir_glob)
    nx, ny = chessboard_size

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((ny * nx, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)

    objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane.

    # Step through the list and search for chessboard corner
    for idx, filename in enumerate(images):
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)

        # If found, add object points, image points
        if ret == True:
            objpoints.append(objp)

            # get better accuracy on the corner locations
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and save images displaying the corners
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            write_name = join(calibration_outputs_dir, "corners_found_" + basename(filename))
            cv2.imwrite(write_name, img)

    img = cv2.imread(images[0])
    img_size = (img.shape[1], img.shape[0])

    # Do camera calibration given object points and image points
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_size, None, None)

    # Undistort image test and save it
    dst = cv2.undistort(img, mtx, dist, None, mtx)
    write_name1 = join(calibration_outputs_dir, 'Undist_' + basename(images[0]))
    cv2.imwrite(write_name1, dst)

    # Save Distortion matrix and coefficient
    write_name2 = join(calibration_outputs_dir, calibration_mtx_dist_filename)
    with open(write_name2, 'wb') as f:
        saved_obj = {"mtx": mtx, "dist": dist}
        pickle.dump(saved_obj, f)

    print("Calibration process complete! Pickled file saved to: [" + write_name2 + "]")
    print("Undistorted image test: from [" + images[0] + "] to [" + basename(write_name1) + "]")
    print("Here is the undistorted image test: [" + write_name1 + "]")


if __name__ == '__main__':
    get_images()
    calibrate_camera_and_pickle_mtx_dist()

