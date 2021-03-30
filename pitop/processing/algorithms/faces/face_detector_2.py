import os
import cv2
import dlib
from .face_utils import get_face_angle
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


class FaceDetector2:
    def __init__(self):
        """
        :param process_image_width: image width to scale to for image processing
        :param input_format: input image format
        :param output_format: output image format
        """
        self._detector = dlib.get_frontal_face_detector()
        self._predictor = dlib.shape_predictor(os.path.join(abs_file_path, predictor_file_name))
        self._frame_resolution = None

    def detect(self, frame):

        if self._frame_resolution is None:
            height, width = frame.shape[0:2]
            self._frame_resolution = (width, height)

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        clahe = cv2.createCLAHE(clipLimit=5)
        gray = clahe.apply(gray)

        left = 0
        top = 0
        right = 48
        bottom = 48

        rectangle_dlib = dlib.rectangle(left, top, right, bottom)

        face_rectangle, face_center, face_features = self.__process_rectangles(gray, rectangle_dlib)

        if face_features is not None:
            face_found = True
            robot_view = frame.copy()
            self.__draw_on_frame(robot_view, face_rectangle, face_center, face_features)
            rectangle_dimensions = face_rectangle[2:4]
            face_angle = get_face_angle(face_features)
        else:
            face_found = False
            robot_view = frame
            rectangle_dimensions = None
            face_angle = None

        return DotDict({
            "found": face_found,
            "center": face_center,
            "robot_view": robot_view,
            "features": face_features,
            "angle": face_angle,
            "dimensions": rectangle_dimensions
        })

    def __process_rectangles(self, gray, rectangle_dlib):
        x, y, w, h = face_utils.rect_to_bb(rectangle_dlib)
        largest_rectangle_dlib = rectangle_dlib
        face_rectangle = (x, y, w, h)
        face_center = (int(x + w / 2), int(y + h / 2))

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
