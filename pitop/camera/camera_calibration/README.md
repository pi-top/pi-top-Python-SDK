# Camera Calibration
For some computer vision applications, it will ne necessary to remove the distortion from the camera images.

This folder contains all the necessary code and assets to find the camera distortion coefficients and the camera matrix.

For more information, see [this OpenCV tutorial.](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)

## How to carry out calibration
Assuming you have already cloned the project examples directory onto your pi-top [4] and run the setup.py, carry out the following steps:

1. Download the chessboard PDF and print it out onto A4 paper
   * Make sure no scaling is applied by the printer settings.
   * For more chessboard patterns, see [here.](https://markhedleyjones.com/projects/calibration-checkerboard-collection)
1. Place the chessboard onto a flat surface, ideally one with minimal background noise.
1. Plug in your pi-top Camera Module into one of the pi-top [4]'s USB ports.
1. `cd` into the `camera_calibration` directory
1. run `python3 camera_calibration.py`
   1. A preview of the camera frame will display on screen (use VNC or a HDMI display to see)
   1. Take 20 photos using the circle button on the pi-top [4]. 
   1. Get as many perspectives as possible and vary the distance between: filling the frame with the chessboard and; chessboard taking up about half of the frame.
1. Once the `get_images` function has finished, the main calibration function will automatically start.
1. Check the images in the `calibration_output` folder to ensure the points are drawn accurately and that the test image appears to have no distortion on it.


## How to calibrate an image (or video stream) in your projects
The following code will apply the calibration parameters to a frame taken from the pi-top camera module (or whatever camera you used to generate the calibration parameters)
```python
import cv2
from ptrobot.camera_calibration.load_parameters import load_camera_cal
mtx, dist = load_camera_cal()
undistorted_frame = cv2.undistort(frame, mtx, dist, None, mtx)
```

Remember that this calibration is specific to the camera you used. For stringent applications, you may want to re-calibrate even if you swap to another camera of the same model.