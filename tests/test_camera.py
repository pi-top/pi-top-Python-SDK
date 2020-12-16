from threading import Thread
from unittest import (
    TestCase,
    skip
)
from sys import modules
from unittest.mock import Mock
from time import sleep, perf_counter

modules["io"] = Mock()
modules["cv2"] = Mock()
modules["PyV4L2Camera"] = Mock()
modules["PyV4L2Camera.camera"] = Mock()
modules["PyV4L2Camera.exceptions"] = Mock()
modules["imageio"] = Mock()
modules["PIL"] = Mock()
modules["pitop.camera.pil_opencv_conversion"] = Mock()

# import after applying mocks
from pitop.camera.core import (  # noqa: E402
    FrameHandler,
    CaptureActions,
    UsbCamera,
    FileSystemCamera,
    CameraTypes
)
from pitop.camera import Camera  # noqa: E402


class CameraTestCase(TestCase):
    def test_uses_usb_camera_by_default(self):
        c = Camera(4)
        self.assertIsInstance(c._camera, UsbCamera)

    def test_uses_file_system_camera_if_required(self):
        c = Camera(camera_type=CameraTypes.FILE_SYSTEM_CAMERA, path_to_images="/")
        self.assertIsInstance(c._camera, FileSystemCamera)

    def test_from_file_system_classmethod(self):
        c = Camera.from_file_system(path_to_images="/")
        self.assertIsInstance(c._camera, FileSystemCamera)

    def test_from_usb(self):
        c = Camera.from_usb()
        self.assertIsInstance(c._camera, UsbCamera)

    def test_has_frame_handler_attribute(self):
        c = Camera()
        self.assertIsInstance(c._frame_handler, FrameHandler)

    def test_runs_thread_to_process_images(self):
        c = Camera()
        self.assertIsInstance(c._process_image_thread, Thread)
        self.assertTrue(c._process_image_thread.is_alive())

    def test_stops_background_thread_by_changing_an_attribute(self):
        c = Camera()
        c._continue_processing = False
        sleep(1)
        self.assertFalse(c._process_image_thread.is_alive())

    @skip
    def test_stops_background_thread_if_camera_is_not_opened(self):
        c = Camera()
        c._camera.is_opened = Mock()
        c._camera.is_opened.return_value = False
        sleep(1)
        self.assertFalse(c._process_image_thread.is_alive())

    def test_current_frame_opencv(self):
        c = Camera(4)
        frame = c.current_frame(format='OpenCV')
        self.assertIsInstance(frame, Mock)

    def test_current_frame_does_not_block(self):
        c = Camera(4)
        start = perf_counter()
        c.current_frame()
        c.current_frame()
        end = perf_counter()
        self.assertTrue(end - start < 0.01)

    def test_get_frame_does_block(self):
        c = Camera(4)
        c._new_frame_event.clear()
        start = perf_counter()
        c.get_frame()
        c.get_frame()
        end = perf_counter()
        self.assertTrue(end - start > 0.01)

    def test_capture_image_registers_action_on_frame_handler(self):
        c = Camera()
        c.capture_image()
        self.assertTrue(c._frame_handler.is_running_action(CaptureActions.CAPTURE_SINGLE_FRAME))

    def test_start_video_capture_registers_action_on_frame_handler(self):
        c = Camera()
        c.start_video_capture()
        self.assertTrue(c._frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE))

    def test_stop_video_capture_removes_action_on_frame_handler(self):
        c = Camera()
        c.start_video_capture()
        c.stop_video_capture()
        self.assertFalse(c._frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE))

    def test_start_detecting_motion_registers_action_on_frame_handler(self):
        c = Camera()

        def callback(frame):
            return
        c.start_detecting_motion(callback)
        self.assertTrue(c._frame_handler.is_running_action(CaptureActions.DETECT_MOTION))

    def test_stop_detecting_motion_removes_action_on_frame_handler(self):
        c = Camera()

        def callback(frame):
            return
        c.start_detecting_motion(callback)
        c.stop_detecting_motion()
        self.assertFalse(c._frame_handler.is_running_action(CaptureActions.DETECT_MOTION))

    def test_start_detecting_motion_fails_when_using_incorrect_callback(self):
        c = Camera()

        def callback(a, b):
            return
        with self.assertRaises(ValueError):
            c.start_detecting_motion(callback)

    def test_start_handling_frames_registers_action_on_frame_handler(self):
        c = Camera()

        def callback(frame):
            return
        c.start_handling_frames(callback)
        self.assertTrue(c._frame_handler.is_running_action(CaptureActions.HANDLE_FRAME))

    def test_stop_handling_frames_motion_removes_action_on_frame_handler(self):
        c = Camera()

        def callback(frame):
            return
        c.start_handling_frames(callback)
        c.stop_handling_frames()
        self.assertFalse(c._frame_handler.is_running_action(CaptureActions.HANDLE_FRAME))

    def test_start_handling_frames_fails_when_using_incorrect_callback(self):
        c = Camera()

        def callback(a, b):
            return
        with self.assertRaises(ValueError):
            c.start_handling_frames(callback)
