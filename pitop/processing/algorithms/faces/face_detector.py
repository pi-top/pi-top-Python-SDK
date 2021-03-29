import os
import cv2
import dlib
from pitop.processing.utils.vision_functions import (
    resize,
    center_reposition
)
from .face_utils import get_face_angle
from pitop.core import ImageFunctions
from imutils import face_utils

# directory where calibration output pickle file is located
classifier_dir = 'predictors'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, classifier_dir)

# Filename for predictor
predictor_file_name = "shape_predictor_68_face_landmarks.dat"


class DotDict(dict):
    """dot.notation access to dictionary attributes."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FaceDetector:
    def __init__(self, process_image_width: int = 320, input_format: str = "PIL", output_format: str = "PIL"):
        """
        :param process_image_width: image width to scale to for image processing
        :param input_format: input image format
        :param output_format: output image format
        """
        self._process_image_width = process_image_width
        self._input_format = input_format
        self._output_format = output_format
        self._detector = dlib.get_frontal_face_detector()
        self._predictor = dlib.shape_predictor(os.path.join(abs_file_path, predictor_file_name))
        self._frame_resolution = None

    def detect(self, frame):

        if self._input_format.lower() == "pil":
            cv_frame = ImageFunctions.convert(frame, format='OpenCV')
        else:
            cv_frame = frame

        cv_frame = resize(cv_frame, width=self._process_image_width)

        if self._frame_resolution is None:
            height, width = cv_frame.shape[0:2]
            self._frame_resolution = (width, height)

        gray = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2GRAY)

        rectangles_dlib = self._detector(gray, 0)

        face_rectangle, face_center, face_features = self.__process_rectangles(gray, rectangles_dlib)

        if face_rectangle is not None:
            face_found = True
            robot_view = cv_frame.copy()
            self.__draw_on_frame(robot_view, face_rectangle, face_center, face_features)
            face_center = center_reposition(face_center, cv_frame)  # has to be done after OpenCV draw functions
            rectangle_dimensions = face_rectangle[2:4]
            face_angle = get_face_angle(face_features)
        else:
            face_found = False
            robot_view = cv_frame
            rectangle_dimensions = None
            face_angle = None

        if self._output_format.lower() == "pil":
            robot_view = ImageFunctions.convert(robot_view, format='PIL')

        return DotDict({
            "found": face_found,
            "center": face_center,
            "robot_view": robot_view,
            "features": face_features,
            "angle": face_angle,
            "rectangle_dimensions": rectangle_dimensions
        })

    def __process_rectangles(self, gray, rectangles_dlib):
        area = 0
        largest_rectangle_dlib = None
        face_rectangle = None
        face_center = None
        for (i, rectangle_dlib) in enumerate(rectangles_dlib):
            x, y, w, h = face_utils.rect_to_bb(rectangle_dlib)
            current_area = w * h
            if current_area > area:
                area = current_area
                largest_rectangle_dlib = rectangle_dlib
                face_rectangle = (x, y, w, h)
                face_center = (int(x + w / 2), int(y + h / 2))

        face_features = None
        if largest_rectangle_dlib is not None:
            face_features_dlib = self._predictor(gray, largest_rectangle_dlib)
            face_features = face_utils.shape_to_np(face_features_dlib)

        return face_rectangle, face_center, face_features

    @staticmethod
    def __draw_on_frame(frame, face_rectangle, face_center, face_features):
        x, y, w, h = face_rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.drawMarker(frame, face_center, (100, 60, 240), markerType=cv2.MARKER_CROSS, markerSize=20,
                       thickness=4, line_type=cv2.FILLED)
        for (x, y) in face_features:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
