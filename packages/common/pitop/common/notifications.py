import logging
from enum import Enum, auto
from subprocess import CalledProcessError, run

from pitop.common.command_runner import run_command

logger = logging.getLogger(__name__)


class NotificationAction:
    def __init__(self, call_to_action_text, command_str) -> None:
        self.call_to_action_text = call_to_action_text
        self.command_str = command_str


class NotificationActionManager:
    def __init__(self):
        self.actions = list()
        self.default_action = None
        self.close_action = None

    def add_action(self, call_to_action_text, command_str) -> None:
        action = NotificationAction(call_to_action_text, command_str)
        self.actions.append(action)

    def set_default_action(self, command_str) -> None:
        default_action = NotificationAction("", command_str)
        self.default_action = default_action

    def set_close_action(self, command_str) -> None:
        close_action = NotificationAction("", command_str)
        self.close_action = close_action


class NotificationUrgencyLevel(Enum):
    low = auto()
    normal = auto()
    critical = auto()


def send_notification(
    title: str,
    text: str,
    icon_name: str = "",
    timeout: int = 0,
    app_name: str = "",
    notification_id: int = -1,
    actions_manager: NotificationActionManager = None,
    urgency_level: NotificationUrgencyLevel = None,
    capture_notification_id: bool = True,
) -> str:
    # Check that `notify-send-ng` is available, as it's not a hard dependency of the package
    try:
        run(["dpkg-query", "-l", "notify-send-ng"], capture_output=True, check=True)
    except CalledProcessError:
        raise Exception("notify-send-ng not installed")

    cmd = "/usr/bin/notify-send "
    cmd += "--print-id "
    cmd += "--expire-time=" + str(timeout) + " "

    if icon_name:
        cmd += "--icon=" + icon_name + " "

    if notification_id >= 0:
        cmd += "--replace=" + str(notification_id) + " "

    if actions_manager is not None:
        for action in actions_manager.actions:
            cmd += (
                '--action="'
                + action.call_to_action_text
                + ":"
                + action.command_str
                + '" '
            )

        if actions_manager.default_action is not None:
            cmd += (
                "--default-action=" + actions_manager.default_action.command_str + " "
            )

        if actions_manager.close_action is not None:
            cmd += "--close-action=" + actions_manager.close_action.command_str + " "

    if app_name:
        cmd += "--app-name=" + app_name + " "

    if urgency_level is not None:
        cmd += "--urgency=" + urgency_level.name + " "

    cmd += ' "' + title + '" '
    cmd += '"' + text + '"'

    logger.info("notify-send command: {}".format(cmd))

    try:
        resp_stdout = run_command(cmd, 2000, capture_output=capture_notification_id)
    except Exception as e:
        logger.warning("Failed to show message: {}".format(e))
        raise
    return resp_stdout
