from pitop.core import ImageFunctions
import numpy as np
from .face_utils import load_emotion_model
from pitop.core.data_stuctures import DotDict
from pitop.processing.core.math_functions import running_mean
from pitop.processing.core.vision_functions import import_opencv
from imutils import face_utils


cv2 = import_opencv()


class EmotionDetector:
    __MEAN_N = 5

    def __init__(self, format: str = "OpenCV", apply_mean_filter=True):
        self._format = format
        self._apply_mean_filter = apply_mean_filter
        self._emotion_model = load_emotion_model()
        self._emotions = ['Neutral', 'Anger', 'Disgust', 'Happy', 'Sad', 'Surprise']
        if self._apply_mean_filter:
            self._probability_mean_array = np.zeros((self.__MEAN_N, len(self._emotions)), dtype=float)

    def detect(self, face):
        frame = face.original_detection_frame.copy()

        frame = ImageFunctions.convert(frame, format='OpenCV')

        if face.found:
            robot_view = frame.copy()
            emotion_type, emotion_confidence = self.__get_emotion(face)
            self.__draw_on_frame(robot_view, face.rectangle, emotion_type, emotion_confidence, face.features)

        else:
            robot_view = frame
            emotion_type = None
            emotion_confidence = None

        if self._format.lower() == "pil":
            robot_view = ImageFunctions.convert(robot_view, format='PIL')

        return DotDict({
            "robot_view": robot_view,
            "type": emotion_type,
            "confidence": emotion_confidence
        })

    @staticmethod
    def __draw_on_frame(frame, face_rectangle, emotion_type, emotion_confidence, face_features):
        x, y, w, h = face_rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1.5
        font_thickness = 3
        text = f"{round(emotion_confidence * 100)}% {emotion_type}"
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_width, text_height = text_size

        text_x = (x + w // 2) - (text_width // 2)
        text_y = y - 5

        if emotion_confidence < 0.5:
            text_colour = (0, 0, 255)
        elif 0.5 <= emotion_confidence < 0.75:
            text_colour = (0, 165, 255)
        else:
            text_colour = (0, 255, 0)

        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_colour, thickness=font_thickness)

        for (x, y) in face_features:
            cv2.circle(frame, (int(x), int(y)), 2, (0, 0, 255), -1)

    def __get_emotion(self, face):

        def get_feature_vector(features, face_angle):
            # face_feature_mean = features.mean(axis=0)
            # M = cv2.getRotationMatrix2D(tuple(face_feature_mean), -face_angle, 1.0)
            # # M = cv2.getRotationMatrix2D((0, 0), -face_angle, 1.0)
            # ones = np.ones(shape=(len(features), 1))
            # points_ones = np.hstack([features, ones])
            # face_features_rotated = M.dot(points_ones.T).T

            rotation_matrix = np.array([[np.cos(np.radians(face_angle)), -np.sin(np.radians(face_angle))],
                                        [np.sin(np.radians(face_angle)), np.cos(np.radians(face_angle))]])

            face_features_rotated = rotation_matrix.dot(features.T).T
            face_feature_mean = face_features_rotated.mean(axis=0)

            left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
            right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
            left_eye_center = np.mean(face_features_rotated[left_eye_start:left_eye_end], axis=0)
            right_eye_center = np.mean(face_features_rotated[right_eye_start:right_eye_end], axis=0)

            interpupillary_distance = np.linalg.norm(left_eye_center - right_eye_center)

            feature_vector = []
            for landmark in face_features_rotated:
                relative_vector = (landmark - face_feature_mean) / interpupillary_distance
                feature_vector.append(relative_vector[0])
                feature_vector.append(relative_vector[1])

            return np.asarray([feature_vector])

        if len(face.features) != 68:
            raise ValueError("This function is only compatible with dlib's 68 landmark feature")

        X = get_feature_vector(face.features, face.angle)

        probabilities = self._emotion_model.predict_proba(X)[0]

        if self._apply_mean_filter:
            self._probability_mean_array, probabilities = running_mean(self._probability_mean_array, probabilities)
        max_index = np.argmax(probabilities)

        return self._emotions[max_index], round(probabilities[max_index], 2)
