from threading import Thread
from time import perf_counter
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

import numpy
from PIL import Image

from tests.utils import wait_until


class CameraTestCase(TestCase):
    def setUp(self):
        from pitop.camera.core.cameras.file_system_camera import FsImage

        image = FsImage("tests/assets/test_image.png")
        self.cv2_patch = patch("pitop.camera.core.cameras.usb_camera.import_opencv")
        self.cv2_mock = self.cv2_patch.start()

        self.read_mock = MagicMock()
        self.read_mock.read.return_value = [1, image.data]
        self.vc_mock = MagicMock()
        self.vc_mock.VideoCapture.return_value = self.read_mock
        self.cv2_mock.return_value = self.vc_mock
        self.addCleanup(self.cv2_patch.stop)

        from pitop.camera import Camera

        self.Camera = Camera

    def tearDown(self):
        if hasattr(self.Camera, "_camera"):
            self.Camera._camera = None

    def test_uses_usb_camera_by_default(self):
        from pitop.camera.core.cameras.usb_camera import UsbCamera

        c = self.Camera(4)
        self.assertIsInstance(c._camera, UsbCamera)

    def test_uses_file_system_camera_if_required(self):
        from pitop.camera.core import CameraTypes, FileSystemCamera

        c = self.Camera(
            camera_type=CameraTypes.FILE_SYSTEM_CAMERA, path_to_images="tests/assets"
        )
        self.assertIsInstance(c._camera, FileSystemCamera)

    def test_from_file_system_classmethod(self):
        from pitop.camera.core.cameras.file_system_camera import FileSystemCamera

        c = self.Camera.from_file_system(path_to_images="tests/assets")
        self.assertIsInstance(c._camera, FileSystemCamera)

    def test_from_usb(self):
        from pitop.camera.core import UsbCamera

        c = self.Camera.from_usb()
        self.assertIsInstance(c._camera, UsbCamera)

    def test_has_frame_handler_attribute(self):
        from pitop.camera.core import FrameHandler

        c = self.Camera()
        self.assertIsInstance(c._frame_handler, FrameHandler)

    def test_runs_thread_to_process_images(self):
        c = self.Camera()
        wait_until(lambda: c._process_image_thread.is_alive())
        self.assertIsInstance(c._process_image_thread, Thread)

    def test_stops_background_thread_by_changing_an_attribute(self):
        c = self.Camera()
        c._continue_processing = False
        wait_until(lambda: c._process_image_thread.is_alive() is False)

    def test_stops_background_thread_if_camera_is_not_opened(self):
        c = self.Camera()
        self.assertTrue(c._process_image_thread.is_alive())
        c._camera.is_opened = MagicMock(return_value=False)
        wait_until(lambda: c._process_image_thread.is_alive() is False)

    def test_current_frame_pil(self):
        c = self.Camera()
        frame = c.current_frame()
        if frame:
            self.assertIsInstance(frame, Image.Image)

    def test_current_frame_opencv(self):
        c = self.Camera()
        c.format = "OpenCV"
        frame = c.current_frame()

        def update_frame():
            nonlocal frame
            frame = c.current_frame()

        wait_until(
            condition=lambda: frame is not None,
            on_wait=update_frame,
        )

        self.assertIsInstance(frame, numpy.ndarray)

    def test_current_frame_does_not_block(self):
        c = self.Camera(4)
        start = perf_counter()
        c.current_frame()
        c.current_frame()
        end = perf_counter()
        self.assertTrue(end - start < 0.01)

    @skip
    def test_get_frame_does_block(self):
        c = self.Camera()
        c._new_frame_event.clear()
        start = perf_counter()
        c.get_frame()
        c.get_frame()
        end = perf_counter()
        self.assertTrue(end - start > 0.01)

    def test_capture_image_registers_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()
        c.capture_image()
        self.assertTrue(
            c._frame_handler.is_running_action(CaptureActions.CAPTURE_SINGLE_FRAME)
        )

    def test_start_video_capture_registers_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()
        c.start_video_capture()
        self.assertTrue(
            c._frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)
        )

    def test_stop_video_capture_removes_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()
        c.start_video_capture()
        c.stop_video_capture()
        self.assertFalse(
            c._frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)
        )

    def test_start_detecting_motion_registers_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()

        def callback(frame):
            return

        c.start_detecting_motion(callback)
        self.assertTrue(
            c._frame_handler.is_running_action(CaptureActions.DETECT_MOTION)
        )

    def test_stop_detecting_motion_removes_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()

        def callback(frame):
            return

        c.start_detecting_motion(callback)
        c.stop_detecting_motion()
        self.assertFalse(
            c._frame_handler.is_running_action(CaptureActions.DETECT_MOTION)
        )

    def test_start_detecting_motion_fails_when_using_incorrect_callback(self):
        c = self.Camera()

        def callback(a, b):
            return

        with self.assertRaises(ValueError):
            c.start_detecting_motion(callback)

    def test_handling_frames_registers_action_on_frame_handler(self):
        from pitop.camera.core import CaptureActions

        c = self.Camera()

        def callback(frame):
            return

        c.start_handling_frames(callback)
        self.assertTrue(c._frame_handler.is_running_action(CaptureActions.HANDLE_FRAME))

        c.stop_handling_frames()
        self.assertFalse(
            c._frame_handler.is_running_action(CaptureActions.HANDLE_FRAME)
        )

    def test_start_handling_frames_fails_when_using_incorrect_callback(self):
        c = self.Camera()
        with self.assertRaises(ValueError):
            c.start_handling_frames(callback_on_frame=lambda: 1)
