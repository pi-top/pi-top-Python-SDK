from sys import modules
from unittest.mock import Mock
import os


modules_to_patch = [
    "imageio",
    "pitopcommon.ptdm",
    "pitopcommon.smbus_device",
    "PyV4L2Camera.camera",
    "PyV4L2Camera.exceptions",
]
for module in modules_to_patch:
    modules[module] = Mock()

# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]

from unittest import TestCase
import numpy as np
import cv2
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionClassifier,
)
from imutils import rotate, resize


face_image_dir = 'assets/face_images'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, face_image_dir)

# emotion_data is [Expected Emotion, Minimum Confidence]
emotion_data = [['Neutral', 0.4], ['Anger', 0.7], ['Disgust', 0.7], ['Happy', 0.9], ['Sad', 0.9], ['Surprise', 0.9]]
face_filenames = ["neutral.jpg", "anger.jpg", "disgust.jpg", "happy.jpg", "sad.jpg", "surprise.jpg"]


class TestFaceAndEmotionDetector(TestCase):

    def setUp(self):
        self._height = 480
        self._width = 640
        self._image_processing_width = 320
        self._frame_scaler = self._width / self._image_processing_width
        self._MAX_FACE_CENTER_DIFFERENCE = self._height // 8  # will ensure center not off by processing scale factor
        self._MAX_FACE_ANGLE_DIFFERENCE = 3
        self._face_rotate_angle = 7.5
        self._blank_cv_frame = np.ones((self._height, self._width, 3), np.uint8) * 255
        self._n = 0

        # get list of images for testing
        self._face_image_data = []
        self._face_images_cw_rotate_data = []
        self._face_images_ccw_rotate_data = []
        for face_filename in face_filenames:
            face_image = cv2.imread(os.path.join(abs_file_path, face_filename))
            face_image = resize(face_image, width=300)
            face_image_height, face_image_width = face_image.shape[0:2]
            merged_image = self._blank_cv_frame.copy()
            x_offset = (self._width - face_image_width) // 2
            y_offset = (self._height - face_image_height) // 2
            merged_image[y_offset:y_offset + face_image_height, x_offset:x_offset + face_image_width, :] = face_image

            self._face_image_data.append([merged_image, face_image_width])

            clockwise_image = rotate(merged_image, -self._face_rotate_angle)
            counterclockwise_image = rotate(merged_image, self._face_rotate_angle)

            self._face_images_cw_rotate_data.append([clockwise_image, face_image_width])
            self._face_images_ccw_rotate_data.append([counterclockwise_image, face_image_width])

    def test_detect_face(self):
        self.detections(self._face_image_data)

    def test_rotated_faces(self):
        self.detections(self._face_images_cw_rotate_data, rotation="cw")
        self.detections(self._face_images_ccw_rotate_data, rotation="ccw")

    def test_no_face(self):
        face_detector = FaceDetector(enable_tracking=False)

        # for test image set this needs to be zero, in normal use it doesn't matter because of filtering
        face_detector._FACE_DETECTOR_PYRAMID_LAYERS = 0

        emotion_classifier = EmotionClassifier(apply_mean_filter=False)
        frame = self._blank_cv_frame.copy()

        face = face_detector(frame)

        self.assertFalse(face.found)
        self.assertIsNone(face.center)
        self.assertIsNone(face.angle)
        self.assertIsNone(face.features)
        self.assertIsNone(face.rectangle)
        self.assertIsNone(face.mouth_dimensions)
        self.assertIsNone(face.left_eye_dimensions)
        self.assertIsNone(face.right_eye_dimensions)
        self.assertIsNone(face.left_eye_center)
        self.assertIsNone(face.right_eye_center)
        self.assertIsNone(face.nose_bottom)
        self.assertIsNone(face.pupil_distance)
        self.assertEqual(face.robot_view.shape[0], self._height)
        self.assertEqual(face.robot_view.shape[1], self._width)

        # check nothing has been drawn to robot view
        comparison = face.robot_view == frame
        self.assertTrue(comparison.all())

        emotion = emotion_classifier(face)

        self.assertIsNone(emotion.type)
        self.assertEqual(emotion.confidence, 0.0)
        self.assertIsInstance(emotion.robot_view, np.ndarray)

        # check nothing has been drawn to robot view
        comparison = emotion.robot_view == frame
        self.assertTrue(comparison.all())

    def detections(self, face_data, rotation=None):
        face_detector = FaceDetector(enable_tracking=False)

        # for test image set this needs to be zero, in normal use it doesn't matter because of filtering
        face_detector._FACE_DETECTOR_PYRAMID_LAYERS = 0

        emotion_classifier = EmotionClassifier(apply_mean_filter=False)

        if rotation == "cw":
            expected_rotation_angle = -self._face_rotate_angle
        elif rotation == "ccw":
            expected_rotation_angle = self._face_rotate_angle
        else:
            expected_rotation_angle = 0

        for i, (frame, width) in enumerate(face_data):
            face = face_detector(frame)
            self.face_assertions(face=face, expected_rotation_angle=expected_rotation_angle, width=width)
            emotion = emotion_classifier(face)
            self.emotion_assertions(emotion=emotion, expected_emotion_data=emotion_data[i], frame=frame)

    def face_assertions(self, face, expected_rotation_angle, width):
        self.assertTrue(face.found)
        for u, v in zip(face.center, (0, 0)):
            self.assertAlmostEqual(u, v, delta=self._MAX_FACE_CENTER_DIFFERENCE)
        self.assertAlmostEqual(face.angle, expected_rotation_angle, delta=self._MAX_FACE_ANGLE_DIFFERENCE)
        self.assertIsInstance(face.robot_view, np.ndarray)
        self.assertEqual(face.robot_view.shape[0], self._height)
        self.assertEqual(face.robot_view.shape[1], self._width)
        self.assertIsInstance(face.original_detection_frame, np.ndarray)
        self.assertEqual(len(face.features), 68)
        self.assertAlmostEqual(face.rectangle[3], width, delta=width // 2)

        # check something has been drawn to robot view
        comparison = face.robot_view == face.original_detection_frame
        self.assertFalse(comparison.all())

    def emotion_assertions(self, emotion, expected_emotion_data, frame):
        self.assertEqual(emotion.type, expected_emotion_data[0])
        self.assertGreaterEqual(emotion.confidence, expected_emotion_data[1])
        self.assertIsInstance(emotion.robot_view, np.ndarray)

        # check something has been drawn to robot view
        comparison = emotion.robot_view == frame
        self.assertFalse(comparison.all())

    def test_calculated_face_data_68_landmark(self):
        face_detector = FaceDetector(enable_tracking=False)
        # for test image set this needs to be zero, in normal use it doesn't matter because of filtering
        face_detector._FACE_DETECTOR_PYRAMID_LAYERS = 0

        test_image = self._face_image_data[0][0]

        face = face_detector(test_image)

        self.assertAlmostEqual(face.angle, -0.5, delta=0.1)
        self.assertAlmostEqual(face.pupil_distance, 112.0, delta=3)

        x, y = face.left_eye_center
        self.assertAlmostEqual(x, 371, delta=3)
        self.assertAlmostEqual(y, 197, delta=3)

        x, y = face.right_eye_center
        self.assertAlmostEqual(x, 259, delta=3)
        self.assertAlmostEqual(y, 195, delta=3)

        w, h = face.left_eye_dimensions
        self.assertAlmostEqual(w, 42.2, delta=3)
        self.assertAlmostEqual(h, 18.1, delta=3)

        w, h = face.right_eye_dimensions
        self.assertAlmostEqual(w, 44.2, delta=3)
        self.assertAlmostEqual(h, 18.3, delta=3)

        x, y = face.mouth_center
        self.assertAlmostEqual(x, 312, delta=3)
        self.assertAlmostEqual(y, 311, delta=3)

        w, h = face.mouth_dimensions
        self.assertAlmostEqual(w, 88.0, delta=3)
        self.assertAlmostEqual(h, 24.1, delta=3)

        x, y = face.nose_bottom
        self.assertAlmostEqual(x, 314, delta=3)
        self.assertAlmostEqual(y, 272, delta=3)

    def test_calculated_face_data_5_landmark(self):
        face_detector = FaceDetector(dlib_landmark_predictor_filename="shape_predictor_5_face_landmarks.dat",
                                     enable_tracking=False)
        # for test image set this needs to be zero, in normal use it doesn't matter because of filtering
        face_detector._FACE_DETECTOR_PYRAMID_LAYERS = 0

        test_image = self._face_image_data[0][0]

        face = face_detector(test_image)

        self.assertAlmostEqual(face.angle, -1.1, delta=1.0)
        self.assertAlmostEqual(face.pupil_distance, 108.0, delta=3)

        x, y = face.left_eye_center
        self.assertAlmostEqual(x, 371, delta=3)
        self.assertAlmostEqual(y, 197, delta=3)

        x, y = face.right_eye_center
        self.assertAlmostEqual(x, 259, delta=3)
        self.assertAlmostEqual(y, 195, delta=3)

        w, h = face.left_eye_dimensions
        self.assertAlmostEqual(w, 42.2, delta=3)
        self.assertIsNone(h)

        w, h = face.right_eye_dimensions
        self.assertAlmostEqual(w, 44.2, delta=3)
        self.assertIsNone(h)

        self.assertRaises(ValueError, lambda: face.mouth_center)
        self.assertRaises(ValueError, lambda: face.mouth_dimensions)

        x, y = face.nose_bottom
        self.assertAlmostEqual(x, 314, delta=3)
        self.assertAlmostEqual(y, 276, delta=3)
