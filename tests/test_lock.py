from sys import modules
from threading import Thread
from unittest import TestCase, skip
from unittest.mock import Mock, mock_open, patch

mock_os = modules["os"] = Mock()
mock_logger = modules["pitop.common.logger"] = Mock()

# import after applying mocks
from pitop.common.lock import PTLock  # noqa: E402


@skip
class PTLockTestCase(TestCase):
    __dummy_lock_id = "dummy"
    lock_file_path = "/tmp/.com.pi-top.sdk.dummy.lock"

    def tearDown(self):
        mock_logger.reset_mock()
        mock_os.reset_mock()

    @patch("builtins.open", new_callable=mock_open())
    def test_instance_opens_file(self, m):
        _ = PTLock(self.__dummy_lock_id)
        m.assert_called_with(self.lock_file_path, "w")

    @patch("pitop.common.lock.exists", return_value=True)
    def test_chmod_not_called_if_file_exist(self, exists_mock):
        _ = PTLock(self.__dummy_lock_id)
        exists_mock.assert_called_once_with(self.lock_file_path)
        mock_os.chmod.assert_not_called()

    @patch("pitop.common.lock.exists", return_value=False)
    def test_chmod_is_called_if_file_doesnt_exist(self, exists_mock):
        _ = PTLock(self.__dummy_lock_id)
        exists_mock.assert_called_once_with(self.lock_file_path)
        mock_os.chmod.assert_called_once_with(self.lock_file_path, 146)

    def test_acquire_success(self):
        lock = PTLock(self.__dummy_lock_id)
        self.assertTrue(lock.acquire())

    def test_acquire_an_already_acquired_lock_by_same_object_fails(self):
        lock = PTLock(self.__dummy_lock_id)
        self.assertTrue(lock.acquire())
        self.assertFalse(lock.acquire())

    def test_release_a_locked_lock_by_same_object_returns_true(self):
        lock = PTLock(self.__dummy_lock_id)
        self.assertTrue(lock.acquire())
        self.assertTrue(lock.release())

    def test_release_a_locked_lock_by_other_object_fails(self):
        lock1 = PTLock(self.__dummy_lock_id)
        self.assertTrue(lock1.acquire())

        lock2 = PTLock(self.__dummy_lock_id)
        self.assertFalse(lock2.release())

    def test_release_an_unlocked_lock_returns_false(self):
        lock = PTLock(self.__dummy_lock_id)
        self.assertFalse(lock.release())

    def test_acquire_locks_all_instances(self):
        lock1 = PTLock(self.__dummy_lock_id)
        lock2 = PTLock(self.__dummy_lock_id)

        lock1.acquire()
        for lock in (lock1, lock2):
            self.assertTrue(lock.is_locked())
        lock1.release()

    def test_acquire_locks_thread_until_unlocked(self):
        def acquire_lock(_lock: PTLock):
            _lock.acquire()

        lock = PTLock(self.__dummy_lock_id)
        lock.acquire()

        lock2 = PTLock(self.__dummy_lock_id)
        thread = Thread(target=acquire_lock, args=[lock2])
        thread.start()

        self.assertTrue(thread.is_alive())
        lock.release()
        thread.join()
        self.assertFalse(thread.is_alive())

    def test_is_locked_method(self):
        lock1 = PTLock(self.__dummy_lock_id)
        lock2 = PTLock(self.__dummy_lock_id)

        lock1.acquire()
        for lock in (lock1, lock2):
            self.assertTrue(lock.is_locked())

        lock1.release()
        for lock in (lock1, lock2):
            self.assertFalse(lock.is_locked())
