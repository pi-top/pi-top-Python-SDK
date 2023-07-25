from unittest.mock import MagicMock

from pitop.camera.core import CaptureActions, FrameHandler


def test_capture_actions_empty_when_instantiating():
    """No capture actions are available when instantiating."""
    f = FrameHandler()
    assert len(f._capture_actions) == 0


def test_register_action_success():
    """Register an action."""
    f = FrameHandler()

    action = CaptureActions.CAPTURE_SINGLE_FRAME

    f.register_action(action, {})
    assert len(f._capture_actions) == 1
    assert action in f._capture_actions


def test_capture_frame_action_only_runs_once():
    """Capture single frame only runs once."""
    f = FrameHandler()

    action = CaptureActions.CAPTURE_SINGLE_FRAME

    f.register_action(action, {})
    assert len(f._capture_actions) == 1
    f.process()
    assert len(f._capture_actions) == 0


def test_cant_register_same_action_twice():
    """Can't register same action more than once."""
    f = FrameHandler()

    action = CaptureActions.CAPTURE_VIDEO_TO_FILE

    f.register_action(action, {})
    f.register_action(action, {})
    assert len(f._capture_actions) == 1


def test_remove_action_success():
    """remove_action successfully removes existing actions."""
    f = FrameHandler()

    action = CaptureActions.CAPTURE_SINGLE_FRAME

    f.register_action(action, {})
    assert f.is_running_action(action) is True
    f.remove_action(action)
    assert f.is_running_action(action) is False


def test_remove_action_failure():
    """remove_action doesn't fail when removing non-registered action."""
    f = FrameHandler()
    capture_actions = f._capture_actions
    f.remove_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)
    assert capture_actions == f._capture_actions


def test_remove_action_calls_stop_method_from_action_object():
    """remove_action calls stop() methods from action object."""
    f = FrameHandler()

    action = CaptureActions.CAPTURE_SINGLE_FRAME

    f.register_action(action, {})
    action_object = f._capture_actions.get(action)
    stop_mock = action_object.stop = MagicMock()

    f.remove_action(action)
    stop_mock.assert_called_once()


def test_actions_are_processed_on_process_call():
    def callback():
        print("This is a callback")

    motion_detector_args = {
        "callback_on_motion": callback,
        "moving_object_minimum_area": 1,
    }
    generic_action_args = {
        "callback_on_frame": callback,
        "frame_interval": 1,
        "format": "OpenCV",
    }
    args = {
        CaptureActions.DETECT_MOTION: motion_detector_args,
        CaptureActions.HANDLE_FRAME: generic_action_args,
        CaptureActions.CAPTURE_SINGLE_FRAME: {},
        CaptureActions.CAPTURE_VIDEO_TO_FILE: {},
    }

    f = FrameHandler()
    for action in CaptureActions:
        f.register_action(action, args.get(action))

    mock_arr = []
    for action, action_object in f._capture_actions.items():
        action_object.process = MagicMock()
        mock_arr.append(action_object.process)

    f.process()
    for process_mock in mock_arr:
        process_mock.assert_called_once()
