import os
import cv2
from pitop.processing.utils.vision_functions import (
    find_largest_rectangle,
    resize,
    center_reposition
)
from pitop.core import ImageFunctions

# directory where calibration output pickle file is located
classifier_dir = 'classifiers'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, classifier_dir)

# Filename for classifier
cascade_model_classifier = 'haarcascade_frontalface_default.xml'


class DotDict(dict):
    """dot.notation access to dictionary attributes."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FaceDetector:
    def __init__(self):
        self._face_cascade = cv2.CascadeClassifier(os.path.join(abs_file_path, cascade_model_classifier))
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

        if self._face_found:
            # Limit search area to speed up the framerate if previous face was found
            image_search_rectangle = self.__get_face_search_rectangle(self._face_rectangle)
            x, y, w, h = image_search_rectangle
            cropped_image = gray[y:y + h, x:x + w]
            faces = self._face_cascade.detectMultiScale(cropped_image, 1.1, 4)

            i = 0
            for x_f, y_f, w_f, h_f in faces:
                # convert coordinates to full frame resolution
                x_f = x_f + x
                y_f = y_f + y
                faces[i][0] = x_f
                faces[i][1] = y_f
                i += 1
        else:
            # if no faces previously found then we need to search whole frame
            faces = self._face_cascade.detectMultiScale(gray, 1.1, 4)

        center, self._face_rectangle = self.__process_faces(faces)

        if center is not None:
            self._face_found = True
            robot_view = cv_frame.copy()
            self.__draw_on_frame(robot_view, center, self._face_rectangle)
            center = center_reposition(center, cv_frame)  # has to be done after OpenCV draw functions
            rectangle_dimensions = self._face_rectangle[2:4]
        else:
            self._face_found = False
            robot_view = cv_frame
            rectangle_dimensions = None

        return DotDict({
            "found": self._face_found,
            "center": center,
            "robot_view": robot_view,
            "rectangle_dimensions": rectangle_dimensions
        })

    @staticmethod
    def __process_faces(faces: list):
        if len(faces) != 0:
            largest_face_rectangle = find_largest_rectangle(faces)
            x, y, w, h = largest_face_rectangle
            face_center = (x + int(w/2), y + int(h/2))
        else:
            largest_face_rectangle = None
            face_center = None

        return face_center, largest_face_rectangle

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
    def __draw_on_frame(frame, center, rectangle):
        x, y, w, h = rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.drawMarker(frame, center, (100, 60, 240), markerType=cv2.MARKER_CROSS, markerSize=20,
                       thickness=4, line_type=cv2.FILLED)
