import os
import cv2
import dlib
from pitop.processing.utils.vision_functions import (
    find_largest_rectangle,
    resize,
    center_reposition
)
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


class FaceDetectorDLib:
    def __init__(self):
        self._detector = dlib.get_frontal_face_detector()
        self._predictor = dlib.shape_predictor(os.path.join(abs_file_path, predictor_file_name))
        self._frame_resolution = None
        self._frame = None
        self._face_found = False
        self._face_rectangle = None

    def detect(self, frame):

        cv_frame = ImageFunctions.convert(frame, format='OpenCV')

        cv_frame = resize(cv_frame, width=320)

        if self._frame_resolution is None:
            height, width = cv_frame.shape[0:2]
            self._frame_resolution = (width, height)

        gray = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2GRAY)

        a = 0
        if a:
            # TODO: use dlib object tracker instead of searching from scratch every time
            # https://www.pyimagesearch.com/2018/10/22/object-tracking-with-dlib/

            # Limit search area to speed up the framerate if previous face was found
            image_search_rectangle = self.__get_face_search_rectangle(self._face_rectangle)
            x, y, w, h = image_search_rectangle
            cropped_image = gray[y:y + h, x:x + w]
            rectangles_dlib = self._detector(cropped_image, 0)

            i = 0
            for (i, rectangle_dlib) in enumerate(rectangles_dlib):
                # convert coordinates to full frame resolution
                rectangle_dlib.left += x
                rectangle_dlib.top += y
                rectangle_dlib.right += x
                rectangle_dlib.bottom += y
                # TODO:
        else:
            rectangles_dlib = self._detector(gray, 0)

        face_rectangle, face_center, face_features = self.__process_rectangles(gray, rectangles_dlib)

        if face_rectangle is not None:
            self._face_found = True
            robot_view = cv_frame.copy()
            self.__draw_on_frame(robot_view, face_rectangle, face_center, face_features)
            face_center = center_reposition(face_center, cv_frame)  # has to be done after OpenCV draw functions
            rectangle_dimensions = face_rectangle[2:4]
        else:
            self._face_found = False
            robot_view = cv_frame
            rectangle_dimensions = None

        return DotDict({
            "found": self._face_found,
            "center": face_center,
            "robot_view": robot_view,
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

    def __get_face_search_rectangle(self, previous_face_rectangle: tuple):
        search_scaler = 2
        x, y, w, h = previous_face_rectangle

        w_new = w * search_scaler
        h_new = h * search_scaler
        x_new = x - int((w_new - w) / 2)
        y_new = y - int((h_new - h) / 2)

        # limit x and y to be from 0 to image resolution
        x_new = min(self._frame_resolution[0], max(0, x_new))
        y_new = min(self._frame_resolution[1], max(0, y_new))

        # limit rectangle to lie within bounds of frame
        w_new = min(self._frame_resolution[0] - x_new, w_new)
        h_new = min(self._frame_resolution[1] - y_new, h_new)

        return x_new, y_new, w_new, h_new

    @staticmethod
    def __draw_on_frame(frame, face_rectangle, face_center, face_features):
        x, y, w, h = face_rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.drawMarker(frame, face_center, (100, 60, 240), markerType=cv2.MARKER_CROSS, markerSize=20,
                       thickness=4, line_type=cv2.FILLED)
        for (x, y) in face_features:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
