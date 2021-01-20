from threading import Lock

from .capture_actions import CaptureActions
from pitop.pma.common import type_check


class FrameHandler:
    """
    Class that processes actions performed on a camera frame.
    :data:`CaptureActions` must be registered, alongside an object using the :data:`register_action` method.
    These actions will be run whenever the :data:`process` method is called.
    """

    def __init__(self) -> None:
        self.__capture_actions = {}
        self.__frame = None

        self.__process_lock = Lock()
        self.__frame_lock = Lock()

    @property
    def frame(self):
        with self.__frame_lock:
            f = self.__frame
        return f

    @frame.setter
    def frame(self, frame):
        with self.__frame_lock:
            self.__frame = frame

    def process(self) -> None:
        """
        Executes all the actions registered in the FrameHandler object
        """
        with self.__process_lock:
            frame = self.frame

            capture_actions = self.__capture_actions
            actions_to_remove = [CaptureActions.CAPTURE_SINGLE_FRAME]

            for action_name, action_objects in capture_actions.items():
                try:
                    action_objects.process(frame)
                except Exception as e:
                    print(f"Error processing {action_name}: {e}.")
                    actions_to_remove.append(action_name)

            for action_name in actions_to_remove:
                if self.is_running_action(action_name):
                    self.__capture_actions.pop(action_name)

    @type_check
    def register_action(self, action: CaptureActions, args_dict: dict) -> None:
        """
        Registers an action to be processed when running the :data:`process` method
        Based on the action, an action object instance will be created, using :data:`args_dict` as arguments

        :param CaptureActions action: action to be registered
        :param dict args_dict: dictionary with arguments used to create an action object instance
        """

        if action in self.__capture_actions:
            print("Already registered this action.")
            return
        if "self" in args_dict:
            args_dict.pop("self")

        action_object = action.value(**args_dict)
        self.__capture_actions[action] = action_object

    @type_check
    def remove_action(self, action: CaptureActions) -> None:
        """
        Unregisters an action from the internal action register, to stop being processed when running :data:`process`

        :param CaptureActions action: type of action being removed
        """
        with self.__process_lock:
            if action in self.__capture_actions:
                action_object = self.__capture_actions.pop(action)
                action_object.stop()

    def current_actions(self) -> list:
        """
        Returns a list with the currently registered actions

        :return: list
        """
        return self.__capture_actions.keys()

    @type_check
    def is_running_action(self, action: CaptureActions) -> bool:
        """
        Checks if the given :data:`action` is in the internal action register

        :param CaptureActions action: type of action to check
        :return: bool, True if the action is being processed, False otherwise
        """
        return action in self.__capture_actions
