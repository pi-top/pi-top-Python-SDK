import mmap
import os
from fcntl import flock
from pathlib import Path
from threading import Thread
from time import sleep, time
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

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

    def test_release_unlocks_file_before_thread_lock(self):
        lock = PTLock(self._dummy_lock_id)
        lock.acquire()

        order = []
        thread_lock = lock._thread_lock

        def release_thread_lock():
            order.append("thread")
            thread_lock.release()

        def record_flock(file, operation):
            order.append("file")
            flock(file, operation)

        lock._thread_lock = MagicMock(
            locked=thread_lock.locked, release=release_thread_lock
        )
        with patch("pitop.common.lock.flock", side_effect=record_flock):
            lock.release()

        self.assertEqual(order, ["file", "thread"])

    def test_threads_sharing_a_lock_and_another_process_never_overlap(self):
        # Like pi-topd: two threads share one lock while another process has its own
        shared = mmap.mmap(-1, 2)
        until = time() + 2

        def hold_repeatedly(lock):
            while time() < until:
                with lock:
                    if shared[0]:
                        shared[1] = 1
                    shared[0] = 1
                    sleep(0.0002)
                    shared[0] = 0

        pid = os.fork()
        if pid == 0:
            try:
                hold_repeatedly(PTLock(self._dummy_lock_id))
            finally:
                os._exit(0)

        lock = PTLock(self._dummy_lock_id)
        threads = [Thread(target=hold_repeatedly, args=[lock]) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        os.waitpid(pid, 0)

        self.assertEqual(shared[1], 0)
