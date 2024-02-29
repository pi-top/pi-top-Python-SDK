import numpy as np

from pitop.core import ImageFunctions
from pitop.processing.algorithms.faces.core.emotion import Emotion
from pitop.processing.core.load_models import load_emotion_model
from pitop.processing.core.math_functions import running_mean
from pitop.processing.core.vision_functions import (
    import_face_utils,
    import_opencv,
    tuple_for_color_by_name,
)

cv2 = None
face_utils = None


def import_libs():
    global cv2, face_utils
    if cv2 is None:
        cv2 = import_opencv()
    if face_utils is None:
        face_utils = import_face_utils()


class EmotionClassifier:
    __MEAN_N = 5

    def __init__(self, format: str = "OpenCV", apply_mean_filter=True):
        import_libs()

        self.left_eye_start, self.left_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS[
            "left_eye"
        ]
        self.right_eye_start, self.right_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS[
            "right_eye"
        ]

        self._format = format
        self._apply_mean_filter = apply_mean_filter
        self._emotion_model = load_emotion_model()
        self._onnx_input_node_name = self._emotion_model.get_inputs()[0].name
        self.emotion_types = ["Neutral", "Anger", "Disgust", "Happy", "Sad", "Surprise"]
        self.emotion = Emotion()
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.font_scale = 2
        self.font_thickness = 3
        if self._apply_mean_filter:
            self._probability_mean_array = np.zeros(
                (self.__MEAN_N, len(self.emotion_types)), dtype=float
            )

    def __call__(self, face):
        frame = ImageFunctions.convert(
            face.original_detection_frame.copy(), format="OpenCV"
        )

        if not face.found:
            self.emotion.clear()
            self.emotion.robot_view = frame
            return self.emotion

        self.emotion = self.__get_emotion(frame=frame, face=face, emotion=self.emotion)

        return self.emotion

    def __get_emotion(self, frame, face, emotion):
        """Emotion detection is carried out by taking the 68 face feature
        landmark positions found using the dlib landmark detector and putting
        them through a trained SVC model (in onnx format) that predicts the
        most likely emotion. The prediction outputs probabilities for each
        emotion type which are then put through a moving average filter to
        smooth the output. If being used for non-realtime applications (on
        static images) then the apply_mean_filter class attribute should be set
        to False.

        :param frame: Original camera frame used to detect the face (in
            OpenCV format), used for drawing robot_view.
        :param face: Face object obtained from FaceDetector
        :param emotion: Emotion object to store the resulting prediction
            data
        :return: Emotion object that was passed into this function.
        """

        def get_svc_feature_vector(features, face_angle):
            """The 68 face feature landmark positions need to be put into the
            same format as was used to train the SVC model. The basic process
            is as follows:

                1. Use the face angle to apply a rotation matrix to orient the face features so that the eyes lie on a
                horizontal line.

                2. Find the mean (x, y) coordinate of the resulting face features so we can transform the (x, y)
                face feature coordinates to be zero-centered.

                3. Find the interpupillary distance from the left and right eye center to normalize the (x, y)
                coordinates so that the resulting face features are independent of face scale.

                Note: this will not normalize the face features to lie between 0 and 1 as is typically done when
                pre-processing data to go into a machine learning algorithm. Previously, the diagonal of the face
                rectangle was used to accomplish this but because the face rectangle from face detection comes in
                discreet sizes (based on the pyramid layers), this had poor performance because a continuous scaling
                factor is desired. Interpupillary distance is a good metric since the variance across humans is quite
                small, and the data used for training contains a wide selection of face types to accommodate for this.
                Sklearn's StandardScaler() was added to the SVC pipeline to ensure the data lies between 0 and 1 before
                the classification is carried out - this does not completely remove the need for scaling here as was
                found during testing.

                4. After rotation, transformation and scaling, the resulting (x, y) coordinates are flatted into a numpy
                array in the form array([[x1, y1, x2, y2, ... x68, y68]]) with shape (1, 136). This is now in the format
                 to send to the onnx SVC model for emotion classification.

            :param features: 68 landmark face feature (x, y) coordinates in a 68x2 numpy array (found from FaceDetector)
            :param face_angle: face angle from Face object (found from FaceDetector).
            :return: 1x136 feature vector to put through the onnx SVC model.
            """
            rotation_matrix = np.array(
                [
                    [np.cos(np.radians(face_angle)), -np.sin(np.radians(face_angle))],
                    [np.sin(np.radians(face_angle)), np.cos(np.radians(face_angle))],
                ]
            )

            face_features_rotated = rotation_matrix.dot(features.T).T
            face_feature_mean = face_features_rotated.mean(axis=0)

            left_eye_center = np.mean(
                face_features_rotated[self.left_eye_start : self.left_eye_end], axis=0
            )
            right_eye_center = np.mean(
                face_features_rotated[self.right_eye_start : self.right_eye_end], axis=0
            )

            interpupillary_distance = np.linalg.norm(left_eye_center - right_eye_center)

            feature_vector = []
            for landmark in face_features_rotated:
                relative_vector = (
                    landmark - face_feature_mean
                ) / interpupillary_distance
                feature_vector.append(relative_vector[0])
                feature_vector.append(relative_vector[1])

            return np.asarray([feature_vector])

        if len(face.features) != 68:
            raise ValueError(
                "This function is only compatible with dlib's 68 landmark feature predictor."
            )

        X = get_svc_feature_vector(face.features, face.angle)

        # Run feature vector through onnx model and convert results to a numpy array
        probabilities = np.asarray(
            list(
                self._emotion_model.run(
                    None, {self._onnx_input_node_name: X.astype(np.float32)}
                )[1][0].values()
            )
        )

        if self._apply_mean_filter:
            self._probability_mean_array, probabilities = running_mean(
                self._probability_mean_array, probabilities
            )

        # Get the index of the most likely emotion type and associate to corresponding emotion string
        max_index = int(np.argmax(probabilities))
        emotion.type = self.emotion_types[max_index]
        emotion.confidence = round(probabilities[max_index], 2)

        emotion.robot_view = ImageFunctions.convert(
            self.__draw_on_frame(frame=frame.copy(), face=face, emotion=self.emotion),
            format=self._format,
        )

        return emotion

    def __draw_on_frame(self, frame, face, emotion):
        x, y, w, h = face.rectangle

        text = f"{round(emotion.confidence * 100)}% {emotion.type}"
        text_size = cv2.getTextSize(
            text, self.font, self.font_scale, self.font_thickness
        )[0]

        text_x = (x + w // 2) - (text_size[0] // 2)
        text_y = y - 5

        if emotion.confidence < 0.5:
            text_colour = tuple_for_color_by_name("orangered", bgr=True)
        elif emotion.confidence < 0.75:
            text_colour = tuple_for_color_by_name("orange", bgr=True)
        else:
            text_colour = tuple_for_color_by_name("springgreen", bgr=True)

        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            self.font,
            self.font_scale,
            text_colour,
            thickness=self.font_thickness,
        )

        for x, y in face.features:
            cv2.circle(
                frame,
                (int(x), int(y)),
                2,
                tuple_for_color_by_name("magenta", bgr=True),
                -1,
            )

        return frame
