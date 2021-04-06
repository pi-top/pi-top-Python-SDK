from pitop.core import ImageFunctions
from pitop.camera.camera_calibration.load_parameters import load_camera_cal
import numpy as np
import math
from .face_utils import load_emotion_model
from pitop.core.data_stuctures import DotDict
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()


class EmotionDetector:
    def __init__(self, input_format: str = "PIL", output_format: str = "PIL"):
        self._input_format = input_format
        self._output_format = output_format
        self._mtx = None
        self._dist = None
        self._mtx_new = None
        self._camera_cal_updated = False
        self._emotion_model = load_emotion_model()
        self._emotions = ['Anger', 'Disgust', 'Happy', 'Sad', 'Surprise']

    def detect(self, face):
        frame = face.frame.copy()
        if self._input_format.lower() == "pil":
            frame = ImageFunctions.convert(frame, format='OpenCV')

        # TODO: test calibration with new classifier once finished,, decide whether to keep or not
        if not self._camera_cal_updated:
            height, width = frame.shape[0:2]
            self._mtx, self._dist = load_camera_cal(width=width, height=height)
            self._mtx_new, _ = cv2.getOptimalNewCameraMatrix(self._mtx, self._dist,
                                                             (width, height), 1, (width, height))
            self._camera_cal_updated = True

        if face.found:
            robot_view = frame.copy()
            type, confidence = self._get_emotion(face.features, face.dimensions)
            self.__draw_on_frame(robot_view, face.rectangle, type, confidence)

        else:
            robot_view = frame
            type = None
            confidence = None

        if self._output_format.lower() == "pil":
            robot_view = ImageFunctions.convert(robot_view, format='PIL')

        return DotDict({
            "robot_view": robot_view,
            "type": type,
            "confidence": confidence
        })

    @staticmethod
    def __draw_on_frame(frame, face_rectangle, emotion_type, emotion_confidence):
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

    def _get_emotion(self, face_features, face_dimensions):

        def get_feature_vector(features, normalizer):
            face_feature_mean = features.mean(axis=0)
            # TODO: use face angle to rotate face features before calculating emotion

            feature_vector = []
            for landmark in features:
                relative_vector = (landmark - face_feature_mean) * normalizer
                feature_vector.append(relative_vector[0])
                feature_vector.append(relative_vector[1])

            return np.asarray([feature_vector])

        if len(face_features) != 68:
            raise ValueError("This function is only compatible with dlib's 68 landmark feature")

        normalizer = 1.0 / math.sqrt(face_dimensions[0] ** 2 + face_dimensions[1] ** 2)

        X = get_feature_vector(face_features, normalizer)
        probabilities = self._emotion_model.predict_proba(X)[0]
        max_index = np.argmax(probabilities)

        return self._emotions[max_index], round(probabilities[max_index], 2)

    def __get_undistorted_features(self, face_features):
        face_features_reshaped = face_features.reshape(face_features.shape[0], 1, 2).astype(np.float32)

        face_features_undistorted = cv2.undistortPoints(face_features_reshaped,
                                                        self._mtx, self._dist, None, self._mtx_new)

        face_features_undistorted = face_features_undistorted.reshape(face_features.shape[0], 2).astype(int)

        return face_features_undistorted
