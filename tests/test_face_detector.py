from sys import modules
from unittest.mock import Mock
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
from pitop.processing.algorithms.faces import FaceDetector


face_image_dir = 'assets/face_images'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, face_image_dir)
neutral_face = "neutral.jpg"
happy_face = "happy.jpg"
sad_face = "sad.jpg"
surprise_face = "surprise.jpg"
angry_face = "angry.jpg"
disgust_face = "disgust.jpg"

emotions = ['Neutral', 'Anger', 'Disgust', 'Happy', 'Sad', 'Surprise']
face_filenames = [neutral_face, angry_face, disgust_face, happy_face, sad_face, surprise_face]

# self._neutral_face = cv2.imread(os.path.join(abs_file_path, neutral_face))
#         self._happy_face = cv2.imread(os.path.join(abs_file_path, happy_face))
#         self._sad_face = cv2.imread(os.path.join(abs_file_path, sad_face))
#         self._surprised_face = os.path.join(abs_file_path, surprised_face)
#         self._angry_face = os.path.join(abs_file_path, angry_face)
#         self._disgust_face = os.path.join(abs_file_path, disgust_face)


class TestFaceDetector(TestCase):

    def setUp(self):
        self._height = 320
        self._width = 640
        self._image_processing_width = 320
        self._frame_scaler = self._width / self._image_processing_width
        self._MAX_FACE_CENTER_DIFFERENCE = 15
        self._MAX_FACE_ANGLE_DIFFERENCE = 1
        self._blank_cv_frame = np.zeros((self._height, self._width, 3), np.uint8)
        self._face_images = []
        for face_filename in face_filenames:
            self._face_images.append(cv2.imread(os.path.join(abs_file_path, face_filename)))

    def test_detect_face(self):
        face_detector = FaceDetector()

        for i, face in enumerate(self._face_images):
            face = face_detector.detect(face)
            print(i)
            self.assertTrue(face.found)
            for u, v in zip(face.center, (0, 0)):
                self.assertAlmostEqual(u, v, delta=self._MAX_FACE_CENTER_DIFFERENCE)
            self.assertIsInstance(face.robot_view, np.ndarray)
            self.assertEqual(len(face.features), 68)
            self.assertAlmostEqual(face.angle, 0, delta=self._MAX_FACE_ANGLE_DIFFERENCE)

    def test_rotated_face(self):
        pass

