from pathlib import Path
from threading import Thread
from time import sleep
from unittest import TestCase
from unittest.mock import mock_open, patch

import pytest

from pitop.common.lock import PTLock  # noqa: E402


class PTLockTestCase(TestCase):
    _dummy_lock_id = "dummy"
    lock_file_path = "/tmp/.com.pi-top.sdk.dummy.lock"

    def setUp(self):
        self.chmod_patch = patch("pitop.common.lock.chmod")
        self.chmod_mock = self.chmod_patch.start()
        self.addCleanup(self.chmod_mock.stop)

    def tearDown(self) -> None:
        file = Path(self.lock_file_path)
        if file.exists():
            file.unlink()

    @patch("builtins.open", new_callable=mock_open())
    def test_instance_opens_file(self, m):
        _ = PTLock(self._dummy_lock_id)
        m.assert_called_with(self.lock_file_path, "w")

    @patch("pitop.common.lock.exists", return_value=True)
    def test_chmod_not_called_if_file_exist(self, exists_mock):
        _ = PTLock(self._dummy_lock_id)
        exists_mock.assert_called_once_with(self.lock_file_path)
        self.chmod_mock.assert_not_called()

    @patch("pitop.common.lock.exists", return_value=False)
    def test_chmod_is_called_if_file_doesnt_exist(self, exists_mock):
        _ = PTLock(self._dummy_lock_id)
        exists_mock.assert_called_once_with(self.lock_file_path)
        self.chmod_mock.assert_called_once_with(self.lock_file_path, 146)

    @pytest.mark.flaky(reruns=3)
    def test_is_locked_reports_correct_status(self):
        lock = PTLock(self._dummy_lock_id)
        self.assertFalse(lock.is_locked())
        lock.acquire()
        self.assertTrue(lock.is_locked())

    def test_acquire_locks_other_instances(self):
        lock1 = PTLock(self._dummy_lock_id)
        lock1.acquire()

        lock2 = PTLock(self._dummy_lock_id)
        self.assertTrue(lock2.is_locked())

    def test_only_lock_owner_can_release_lock(self):
        lock1 = PTLock(self._dummy_lock_id)
        lock1.acquire()

        lock2 = PTLock(self._dummy_lock_id)
        self.assertRaises(RuntimeError, lock2.release)

    def test_release_an_unlocked_lock_raises(self):
        lock = PTLock(self._dummy_lock_id)
        self.assertRaises(RuntimeError, lock.release)

    def test_acquire_locks_thread_until_unlocked(self):
        def acquire_lock(_lock: PTLock):
            _lock.acquire()

        lock = PTLock(self._dummy_lock_id)
        lock.acquire()

        lock2 = PTLock(self._dummy_lock_id)
        thread = Thread(target=acquire_lock, args=[lock2], daemon=True)
        thread.start()

        sleep(1)
        # lock in thread is still waiting for it to be released
        self.assertTrue(thread.is_alive())

        lock.release()
        thread.join()
        self.assertFalse(thread.is_alive())
        self.assertTrue(lock2.is_locked())
