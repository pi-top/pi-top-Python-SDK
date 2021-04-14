from pitop.core import ImageFunctions
import numpy as np
import math
from .face_utils import load_emotion_model
from pitop.core.data_stuctures import DotDict
from pitop.processing.utils.math_functions import running_mean
from pitop.processing.core.vision_functions import import_opencv


cv2 = import_opencv()


class EmotionDetector:
    __MEAN_N = 5

    def __init__(self, input_format: str = "PIL", output_format: str = "PIL"):
        self._input_format = input_format
        self._output_format = output_format
        self._emotion_model = load_emotion_model()
        self._emotions = ['Neutral', 'Anger', 'Disgust', 'Happy', 'Sad', 'Surprise']
        self._probability_mean_array = np.zeros((self.__MEAN_N, len(self._emotions)), dtype=float)

    def detect(self, face):
        frame = face.frame.copy()

        if self._input_format.lower() == "pil":
            frame = ImageFunctions.convert(frame, format='OpenCV')

        if face.found:
            robot_view = frame.copy()
            emotion_type, emotion_confidence = self.__get_emotion(face)
            self.__draw_on_frame(robot_view, face.rectangle, emotion_type, emotion_confidence, face.features)

        else:
            robot_view = frame
            emotion_type = None
            emotion_confidence = None

        if self._output_format.lower() == "pil":
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

        def get_feature_vector(features, face_dimensions):
            normalizer = 1.0 / math.sqrt(face_dimensions[0] ** 2 + face_dimensions[1] ** 2)

            face_feature_mean = features.mean(axis=0)
            feature_vector = []
            for landmark in features:
                relative_vector = (landmark - face_feature_mean) * normalizer
                feature_vector.append(relative_vector[0])
                feature_vector.append(relative_vector[1])

            return np.asarray([feature_vector])

        if len(face.features) != 68:
            raise ValueError("This function is only compatible with dlib's 68 landmark feature")

        rotation_matrix = np.array([[np.cos(np.radians(face.angle)), -np.sin(np.radians(face.angle))],
                                    [np.sin(np.radians(face.angle)), np.cos(np.radians(face.angle))]])

        face_features_rotated = rotation_matrix.dot(face.features.T).T

        X = get_feature_vector(face_features_rotated, face.dimensions)
        probabilities = self._emotion_model.predict_proba(X)[0]

        self._probability_mean_array, probabilities_mean = running_mean(self._probability_mean_array, probabilities)
        max_index = np.argmax(probabilities_mean)

        return self._emotions[max_index], round(probabilities[max_index], 2)
