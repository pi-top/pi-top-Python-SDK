import os
import dlib
from pitop.processing.utils.vision_functions import center_reposition
from .face_utils import get_face_angle
from pitop.core import ImageFunctions
from imutils import (
    face_utils,
    resize,
)
from pitop.core.data_stuctures import DotDict
import numpy as np
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()

predictor_dir = 'predictors'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, predictor_dir)
predictor_file_name = "shape_predictor_68_face_landmarks.dat"


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
        self._clahe_filter = cv2.createCLAHE(clipLimit=5)
        self._frame_scaler = None

    def detect(self, frame):
        if self._input_format.lower() == "pil":
            frame = ImageFunctions.convert(frame, format='OpenCV')

        if self._frame_scaler is None:
            height, width = frame.shape[0:2]
            self._frame_scaler = width / self._process_image_width

        resized_frame = resize(frame, width=self._process_image_width)
        gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        gray = self._clahe_filter.apply(gray)

        rectangles_dlib = self._detector(gray, 0)

        face_rectangle, face_center, face_features = self.__process_rectangles(gray, rectangles_dlib)

        if face_rectangle is not None:
            # resize back to original frame resolution
            face_rectangle = tuple((int(item * self._frame_scaler) for item in face_rectangle))
            face_center = tuple((int(item * self._frame_scaler) for item in face_center))
            face_features = (face_features * self._frame_scaler).astype("int")

            face_found = True
            robot_view = frame.copy()
            face_dimensions = face_rectangle[2:4]
            face_angle = get_face_angle(face_features)

            self.__draw_on_frame(robot_view, face_rectangle, face_center, face_features)


            # rotation_matrix = np.array([[np.cos(np.radians(face_angle)), -np.sin(np.radians(face_angle))],
            #                             [np.sin(np.radians(face_angle)), np.cos(np.radians(face_angle))]])
            #
            # # relative_face_features = face_features - face_center
            # face_features = rotation_matrix.dot(face_features.T).T
            # face_rectangle_x = face_rectangle[0]
            # face_rectangle_y = face_rectangle[1]
            #
            # face_rectangle_pos_rotated = rotation_matrix @ np.array([[face_rectangle_x], [face_rectangle_y]])
            #
            # face_rectangle = (int(face_rectangle_pos_rotated[0].item()),
            #                   int(face_rectangle_pos_rotated[1].item()),
            #                   face_rectangle[2],
            #                   face_rectangle[3])


            face_center = center_reposition(face_center, frame)  # has to be done after OpenCV draw functions

        else:
            face_found = False
            robot_view = frame
            face_dimensions = None
            face_angle = None

        if self._output_format.lower() == "pil":
            robot_view = ImageFunctions.convert(robot_view, format='PIL')

        return DotDict({
            "found": face_found,
            "center": face_center,
            "robot_view": robot_view,
            "features": face_features,
            "angle": face_angle,
            "dimensions": face_dimensions,
            "rectangle": face_rectangle,
            "frame": frame
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

        cv2.drawMarker(frame, face_center, (100, 60, 240), markerType=cv2.MARKER_CROSS, markerSize=10,
                       thickness=3, line_type=cv2.FILLED)

        for (x, y) in face_features:
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
