from concurrent.futures import ThreadPoolExecutor
from inspect import signature
from numpy import asarray

from pitop.processing.utils.vision_functions import import_opencv
from .capture_action_base import CaptureActionBase


class MotionDetector(CaptureActionBase):
    """
    Class that implements a motion detection algorithm.
    When motion is detected, a callback function is executed.

    :param function callback_on_motion: A callback function that will be called when motion is detected.
    :param int moving_object_minimum_area: The sensitivity of the motion detection, measured as the area of
    pixels changing between frames that constitutes motion.
    """

    def __init__(self, callback_on_motion, moving_object_minimum_area):
        self.cv2 = import_opencv()

        self.__motion_detect_previous_frame = None
        self.__motion_detect_threshold = moving_object_minimum_area**2
        self.__motion_detect_callback = callback_on_motion
        self.__event_executor = ThreadPoolExecutor()

        callback_signature = signature(callback_on_motion)
        self.callback_has_argument = len(callback_signature.parameters) > 0

    def __del__(self):
        self.stop()

    def process(self, frame):
        frame = asarray(frame)
        # Use greyscale and blurred for motion detection
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        gray = self.cv2.GaussianBlur(gray, (21, 21), 0)

        if self.__motion_detect_previous_frame is None:
            self.__motion_detect_previous_frame = gray
        else:
            diff_frame = self.cv2.absdiff(self.__motion_detect_previous_frame, gray)
            threshold_frame = self.cv2.threshold(diff_frame, 30, 255, self.cv2.THRESH_BINARY)[1]
            threshold_frame = self.cv2.dilate(threshold_frame, None, iterations=2)

            contour_data = self.cv2.findContours(threshold_frame.copy(), self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
            if len(contour_data) == 2:
                # opencv 2
                detected_contours = contour_data[0]
            elif len(contour_data) == 3:
                # opencv 3
                detected_contours = contour_data[1]

            for contour in detected_contours:
                area = self.cv2.contourArea(contour)

                if area > self.__motion_detect_threshold:
                    if self.callback_has_argument:
                        self.__event_executor.submit(self.__motion_detect_callback, frame)
                    else:
                        self.__event_executor.submit(self.__motion_detect_callback)
                    break

    def stop(self):
        if self.__event_executor is not None:
            self.__event_executor.shutdown()
            self.__event_executor = None
