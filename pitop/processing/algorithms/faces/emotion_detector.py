from pitop.core import ImageFunctions
import numpy as np
from .face_utils import load_emotion_model
from pitop.processing.core.math_functions import running_mean
from imutils import face_utils
from pitop.processing.core.vision_functions import (
    import_opencv,
    tuple_for_color_by_name,
)


cv2 = import_opencv()


class Emotion:
    def __init__(self):
        self._type = None
        self._confidence = 0.0
        self._robot_view = None

    def clear(self):
        self.type = None
        self.confidence = 0.0

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def confidence(self):
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        self._confidence = value

    @property
    def robot_view(self):
        return self._robot_view

    @robot_view.setter
    def robot_view(self, value):
        self._robot_view = value

    @property
    def found(self):
        return self.type is not None


left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]


class EmotionDetector:
    __MEAN_N = 5

    def __init__(self, format: str = "OpenCV", apply_mean_filter=True):
        self._format = format
        self._apply_mean_filter = apply_mean_filter
        self._emotion_model = load_emotion_model()
        self._input_name = self._emotion_model.get_inputs()[0].name
        self.emotion_types = ['Neutral', 'Anger', 'Disgust', 'Happy', 'Sad', 'Surprise']
        self.emotion = Emotion()
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.font_scale = 2
        self.font_thickness = 3
        if self._apply_mean_filter:
            self._probability_mean_array = np.zeros((self.__MEAN_N, len(self.emotion_types)), dtype=float)

    def __call__(self, face):
        frame = ImageFunctions.convert(face.original_detection_frame.copy(), format='OpenCV')

        if not face.found:
            self.emotion.clear()
            self.emotion.robot_view = frame
            return self.emotion

        self.emotion = self.__get_emotion(frame=frame, face=face, emotion=self.emotion)

        return self.emotion

    def __get_emotion(self, frame, face, emotion):
        def get_svc_feature_vector(features, face_angle):
            rotation_matrix = np.array([[np.cos(np.radians(face_angle)), -np.sin(np.radians(face_angle))],
                                        [np.sin(np.radians(face_angle)), np.cos(np.radians(face_angle))]])

            face_features_rotated = rotation_matrix.dot(features.T).T
            face_feature_mean = face_features_rotated.mean(axis=0)

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

        X = get_svc_feature_vector(face.features, face.angle)

        probabilities = np.asarray(
            list(
                self._emotion_model.run(None, {self._input_name: X.astype(np.float32)})[1][0].values()
            )
        )

        if self._apply_mean_filter:
            self._probability_mean_array, probabilities = running_mean(self._probability_mean_array, probabilities)

        max_index = int(np.argmax(probabilities))

        emotion.type = self.emotion_types[max_index]
        emotion.confidence = round(probabilities[max_index], 2)

        emotion.robot_view = ImageFunctions.convert(
            self.__draw_on_frame(frame=frame.copy(), face=face, emotion=self.emotion),
            format=self._format
        )

        return emotion

    def __draw_on_frame(self, frame, face, emotion):
        x, y, w, h = face.rectangle

        text = f"{round(emotion.confidence * 100)}% {emotion.type}"
        text_size = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)[0]

        text_x = (x + w // 2) - (text_size[0] // 2)
        text_y = y - 5

        if emotion.confidence < 0.5:
            text_colour = tuple_for_color_by_name("orangered", bgr=True)
        elif emotion.confidence < 0.75:
            text_colour = tuple_for_color_by_name("orange", bgr=True)
        else:
            text_colour = tuple_for_color_by_name("springgreen", bgr=True)

        cv2.putText(frame, text, (text_x, text_y), self.font, self.font_scale, text_colour,
                    thickness=self.font_thickness)

        for (x, y) in face.features:
            cv2.circle(frame, (int(x), int(y)), 2, tuple_for_color_by_name("magenta", bgr=True), -1)

        return frame
