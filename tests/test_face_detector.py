from sys import modules
from unittest.mock import Mock
import unittest
import os


modules_to_patch = [
    "imageio",
    "pitopcommon.ptdm",
    "pitopcommon.smbus_device",
    "PyV4L2Camera.camera",
    "PyV4L2Camera.exceptions",
    "simple_pid",
]
for module in modules_to_patch:
    modules[module] = Mock()


from unittest import TestCase
from pitop.processing.algorithms.ball_detect import BallDetector
from pitop.core.ImageFunctions import convert
from pitop.processing.core.vision_functions import (
    center_reposition,
)


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]

import numpy as np
import cv2
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionDetector,
)
from imutils import rotate_bound, resize


face_image_dir = 'assets/face_images'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, face_image_dir)
emotion_data = [['Neutral', 0.4], ['Anger', 0.75], ['Disgust', 0.75], ['Happy', 0.95], ['Sad', 0.9], ['Surprise', 0.9]]
face_filenames = ["neutral.jpg", "anger.jpg", "disgust_3.jpg", "happy.jpg", "sad_3.jpg", "surprise.jpg"]


class TestFaceAndEmotionDetector(TestCase):

    def setUp(self):
        self._height = 480
        self._width = 640
        self._image_processing_width = 320
        self._frame_scaler = self._width / self._image_processing_width
        self._MAX_FACE_CENTER_DIFFERENCE = self._height // 8  # will ensure center not off by processing scale factor
        self._MAX_FACE_ANGLE_DIFFERENCE = 2
        self._face_rotate_angle = 10
        self._blank_cv_frame = np.ones((self._height, self._width, 3), np.uint8) * 255

        # get list of images for testing
        self._face_image_data = []
        self._face_images_cw_rotate_data = []
        self._face_images_ccw_rotate_data = []
        for face_filename in face_filenames:
            face_image = cv2.imread(os.path.join(abs_file_path, face_filename))
            # face_image = resize(face_image, width=160)
            face_image_height, face_image_width = face_image.shape[0:2]
            merged_image = self._blank_cv_frame.copy()
            x_offset = (self._width - face_image_width) // 2
            y_offset = (self._height - face_image_height) // 2
            merged_image[y_offset:y_offset + face_image_height, x_offset:x_offset + face_image_width, :] = face_image

            self._face_image_data.append([merged_image, face_image_height])
            self._face_images_cw_rotate_data.append(
                [rotate_bound(merged_image, self._face_rotate_angle),
                 face_image_height]
            )
            self._face_images_ccw_rotate_data.append(
                [rotate_bound(merged_image, -self._face_rotate_angle), face_image_height]
            )

    def test_detect_face(self):
        self.detections(self._face_image_data)

    @unittest.skip
    def test_rotated_faces(self):
        # self.detections(self._face_images_cw_rotate_data, rotation="cw")
        self.detections(self._face_images_ccw_rotate_data, rotation="ccw")

    def detections(self, face_data, rotation=None):
        face_detector = FaceDetector()
        emotion_detector = EmotionDetector(apply_mean_filter=False)

        if rotation == "cw":
            expected_rotation_angle = -self._face_rotate_angle
        elif rotation == "ccw":
            expected_rotation_angle = self._face_rotate_angle
        else:
            expected_rotation_angle = 0

        for i, (face, height) in enumerate(face_data):
            face = face_detector.detect(face)
            self.face_assertions(face, expected_rotation_angle, height)
            emotion = emotion_detector.detect(face)
            self.emotion_assertions(emotion, expected_emotion_data=emotion_data[i])

    def face_assertions(self, face, expected_rotation_angle, height):
        self.assertTrue(face.found)
        for u, v in zip(face.center, (0, 0)):
            self.assertAlmostEqual(u, v, delta=self._MAX_FACE_CENTER_DIFFERENCE)
        self.assertIsInstance(face.robot_view, np.ndarray)
        self.assertIsInstance(face.frame, np.ndarray)
        self.assertEqual(len(face.features), 68)
        self.assertAlmostEqual(face.angle, expected_rotation_angle, delta=height // 2)
        self.assertAlmostEqual(face.rectangle[3], height, delta=height // 2)

    def emotion_assertions(self, emotion, expected_emotion_data):
        print(emotion.type, emotion.confidence)
        self.assertEqual(emotion.type, expected_emotion_data[0])
        self.assertGreaterEqual(emotion.confidence, expected_emotion_data[1])
        self.assertIsInstance(emotion.robot_view, np.ndarray)

