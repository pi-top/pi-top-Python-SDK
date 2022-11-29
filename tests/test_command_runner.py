from shlex import split
from subprocess import DEVNULL, CalledProcessError, TimeoutExpired
from unittest import TestCase
from unittest.mock import Mock, patch


class RunCommandTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("pitop.common.command_runner.__get_env")
    @patch("pitop.common.command_runner.run")
    def test_run_command_with_lower_priority(self, run_mock, environ_mock):
        environ_mock.return_value = None
        response = Mock()
        response.stdout = b"output of the command"
        response.stderr = b""
        run_mock.return_value = response

        from pitop.common.command_runner import run_command

        command = "ls"
        run_command(command, timeout=10, lower_priority=True)

        run_mock.assert_called_once_with(
            split(f"nice -n 10 {command}"),
            check=True,
            capture_output=True,
            timeout=10,
            env=None,
        )

    @patch("pitop.common.command_runner.logger")
    @patch("pitop.common.command_runner.__get_env")
    @patch("pitop.common.command_runner.run")
    def test_run_command_logs_if_capture_output_is_set(
        self, run_mock, environ_mock, logger_mock
    ):
        response = Mock()
        response.stdout = b"output of the command"
        response.stderr = b""
        run_mock.return_value = response

        from pitop.common.command_runner import run_command

        command = "ls"
        run_command(command, timeout=10, capture_output=True)

        logger_mock.debug.assert_any_call(
            f"run_command(command_str='{command}', timeout=10, check='True', capture_output='True') stderr:\n{str(response.stderr, 'utf8')}"
        )
        logger_mock.debug.assert_any_call(
            f"run_command(command_str='{command}', timeout=10, check='True', capture_output='True') stdout:\n{str(response.stdout, 'utf8')}"
        )

    @patch("pitop.common.command_runner.logger")
    @patch("pitop.common.command_runner.run")
    def test_run_command_logs_on_error(self, run_mock, logger_mock):
        message = "oh oh, there was an error"
        run_mock.side_effect = Exception(message)

        from pitop.common.command_runner import run_command

        command = "ls"
        run_command(command, timeout=10)

        logger_mock.error.assert_called_once_with(f"{message}")

    @patch("pitop.common.command_runner.run")
    def test_run_command_returns_empty_string_on_error(self, run_mock):
        message = "oh oh, there was an error"
        run_mock.side_effect = Exception(message)

        from pitop.common.command_runner import run_command

        command = "ls"
        assert run_command(command, timeout=10) == ""

    @patch("pitop.common.command_runner.run")
    def test_run_command_raises_on_timeout(self, run_mock):
        run_mock.side_effect = TimeoutExpired("oh oh", 1)

        from pitop.common.command_runner import run_command

        command = "ls"
        with self.assertRaises(TimeoutExpired):
            run_command(command, timeout=10)

    @patch("pitop.common.command_runner.run")
    def test_run_command_raises_on_called_process_error(self, run_mock):
        run_mock.side_effect = CalledProcessError(0, "oh oh")

        from pitop.common.command_runner import run_command

        command = "ls"
        with self.assertRaises(CalledProcessError):
            run_command(command, timeout=10)

    @patch("pitop.common.command_runner.__get_env")
    @patch("pitop.common.command_runner.Popen")
    def test_run_command_in_background_doesnt_print_output_by_default(
        self, popen_mock, environ_mock
    ):
        environ_mock.return_value = None
        from pitop.common.command_runner import run_command_background

        command = "ls"
        run_command_background(command)

        popen_mock.assert_called_once_with(
            split(command), stderr=DEVNULL, stdout=DEVNULL, env=None
        )
