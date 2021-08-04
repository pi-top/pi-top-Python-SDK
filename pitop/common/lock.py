from fcntl import flock, LOCK_EX, LOCK_NB, LOCK_UN
from os import chmod
from os.path import exists
from stat import (
    S_IWUSR,
    S_IWGRP,
    S_IWOTH,
)
from threading import Lock

from pitop.common.logger import PTLogger


class PTLock(object):
    __lock_file_handle = None
    __locked_by_self = False

    def __init__(self, id):
        self.path = "/tmp/%s.lock" % id

        self._thread_lock = Lock()

        lock_file_already_existed = exists(self.path)
        self.__lock_file_handle = open(self.path, "w")
        if not lock_file_already_existed:
            chmod(self.path, S_IWUSR | S_IWGRP | S_IWOTH)

        PTLogger.debug("Creating PTLock with path: {}".format(self.path))

    def acquire(self) -> bool:
        """Block until lock can be acquired."""
        if self._thread_lock.locked():
            PTLogger.debug("Attempting to acquire thread lock, which is currently already acquired.")

        if self.is_locked():
            PTLogger.debug(f"Attempting to acquire lock file ({self.path}), which is currently already globally acquired.")

        PTLogger.debug("Acquiring thread lock")
        self._thread_lock.acquire()
        PTLogger.debug("Acquiring lock file at {}".format(self.path))
        flock(self.__lock_file_handle, LOCK_EX)
        self.__locked_by_self = True

    def release(self) -> bool:
        """Attempt to release lock."""
        if not self._thread_lock.locked():
            PTLogger.debug("Attempting to release thread lock, which is currently already acquired.")

        if not self.is_locked():
            PTLogger.debug(f"Attempting to release lock file ({self.path}), which is currently already globally acquired.")

        PTLogger.debug("Releasing thread lock")
        self._thread_lock.release()
        PTLogger.debug("Releasing lock file at {}".format(self.path))
        flock(self.__lock_file_handle, LOCK_UN)
        self.__locked_by_self = False

    def is_locked(self):
        if self.__locked_by_self:
            return self.__locked_by_self

        lock_status = False
        try:
            flock(self.__lock_file_handle, LOCK_EX | LOCK_NB)
            flock(self.__lock_file_handle, LOCK_UN)
        except BlockingIOError:
            lock_status = True

        PTLogger.debug("Lock file at {} is {}locked".format(
            self.path, "not " if not lock_status else ""))
        return lock_status

    __enter__ = acquire

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def __del__(self):
        if self.__lock_file_handle:
            self.__lock_file_handle.close()
