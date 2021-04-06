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
from pitop.camera.camera_calibration.load_parameters import load_camera_cal
import numpy as np
import math
from .face_utils import load_emotion_model
from pitop.core.data_stuctures import DotDict

# directory where calibration output pickle file is located
classifier_dir = 'predictors'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, classifier_dir)

# Filename for predictor
predictor_file_name = "shape_predictor_68_face_landmarks.dat"


class EmotionDetector:
    def __init__(self):
        self._mtx = None
        self._dist = None
        self._mtx_new = None
        self._camera_cal_updated = False
        self._emotion_model = load_emotion_model()
        self._emotions = ['anger', 'disgust', 'happy', 'sadness', 'surprise']

    def detect(self, face):
        if not self._camera_cal_updated:
            height, width = frame.shape[0:2]
            self._mtx, self._dist = load_camera_cal(width=width, height=height)
            self._mtx_new, self._roi = cv2.getOptimalNewCameraMatrix(self._mtx, self._dist,
                                                                     (width, height), 1, (width, height))
            self._camera_cal_updated = True

        undistorted_frame = cv2.undistort(frame, self._mtx, self._dist, None, self._mtx_new)

        # crop to roi
        x, y, w, h = self._roi
        undistorted_frame = undistorted_frame[y:y+h, x:x+w]

        resized_frame = resize(undistorted_frame, width=self._process_image_width)
        gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        gray = self._clahe_filter.apply(gray)

        rectangles_dlib = self._detector(gray, 0)

        face_rectangle, face_center, face_features = self.__process_rectangles(gray, rectangles_dlib)

        if face_rectangle is not None:
            face_found = True
            robot_view = resized_frame.copy()
            face_dimensions = face_rectangle[2:4]
            face_angle = get_face_angle(face_features)
            emotion = self._get_emotion(face_features, face_dimensions)
            self.__draw_on_frame(robot_view, face_rectangle, face_center, face_features, emotion)
            face_center = center_reposition(face_center, resized_frame)  # has to be done after OpenCV draw functions

        else:
            face_found = False
            robot_view = resized_frame
            face_dimensions = None
            face_angle = None
            emotion = None

        if self._output_format.lower() == "pil":
            robot_view = ImageFunctions.convert(robot_view, format='PIL')

        return DotDict({
            "found": face_found,
            "center": face_center,
            "robot_view": robot_view,
            "features": face_features,
            "angle": face_angle,
            "dimensions": face_dimensions,
            "emotion": emotion
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
    def __draw_on_frame(frame, face_rectangle, face_center, face_features, emotion):
        x, y, w, h = face_rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1.2
        font_thickness = 2
        text = f"{round(emotion.confidence * 100)}% {emotion.type}"
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_width, text_height = text_size

        text_x = (x + w // 2) - (text_width // 2)
        text_y = y - 5

        if emotion.confidence < 0.5:
            text_colour = (0, 0, 255)
        elif 0.5 <= emotion.confidence < 0.75:
            text_colour = (0, 165, 255)
        else:
            text_colour = (0, 255, 0)

        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_colour, thickness=font_thickness)

        cv2.drawMarker(frame, face_center, (100, 60, 240), markerType=cv2.MARKER_CROSS, markerSize=10,
                       thickness=2, line_type=cv2.FILLED)
        for (x, y) in face_features:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

    def _get_emotion(self, face_features, face_dimensions):

        def get_feature_vector(features, normalizer):
            face_feature_mean = features.mean(axis=0)

            feature_vector = []
            for landmark in features:
                relative_vector = (landmark - face_feature_mean) * normalizer
                feature_vector.append(relative_vector[0])
                feature_vector.append(relative_vector[1])

            return np.asarray([feature_vector])

        if len(face_features) != 68:
            raise ValueError("This function is only compatible with dlib's 68 landmark feature")

        normalizer = 1.0 / math.sqrt(face_dimensions[0] ** 2 + face_dimensions[1] ** 2)

        # TODO: use face angle to rotate face features before calculating emotion
        X = get_feature_vector(face_features, normalizer)
        probabilities = self._emotion_model.predict_proba(X)[0]
        max_index = np.argmax(probabilities)

        return DotDict({
            "type": self._emotions[max_index],
            "confidence": round(probabilities[max_index], 2)
        })
