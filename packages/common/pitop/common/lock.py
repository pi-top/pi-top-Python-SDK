import logging
from fcntl import LOCK_EX, LOCK_NB, LOCK_UN, flock
from os import chmod
from os.path import exists
from stat import S_IWGRP, S_IWOTH, S_IWUSR
from threading import Lock

logger = logging.getLogger(__name__)


class PTLock(object):
    __lock_file_handle = None
    __locked_by_self = False

    def __init__(self, id):
        self.path = f"/tmp/.com.pi-top.sdk.{id}.lock"

        self._thread_lock = Lock()

        lock_file_already_existed = exists(self.path)
        self.__lock_file_handle = open(self.path, "w")
        if not lock_file_already_existed:
            chmod(self.path, S_IWUSR | S_IWGRP | S_IWOTH)

        logger.debug("Creating PTLock with path: {}".format(self.path))

    def acquire(self) -> bool:
        """Block until lock can be acquired."""
        logger.debug("Acquiring thread lock")
        self._thread_lock.acquire()
        logger.debug("Acquiring lock file at {}".format(self.path))
        flock(self.__lock_file_handle, LOCK_EX)
        self.__locked_by_self = True

    def release(self) -> bool:
        """Attempt to release lock."""
        if not self._thread_lock.locked():
            raise RuntimeError("release unlocked lock")

        # Unlock the file before the thread lock. The other way round, a thread
        # waiting on this instance gets in while the file is still locked, and
        # this unlock then leaves it running unprotected.
        logger.debug("Releasing lock file at {}".format(self.path))
        self.__locked_by_self = False
        flock(self.__lock_file_handle, LOCK_UN)
        logger.debug("Releasing thread lock")
        self._thread_lock.release()

    def is_locked(self):
        if self.__locked_by_self:
            return self.__locked_by_self

        lock_status = False
        try:
            flock(self.__lock_file_handle, LOCK_EX | LOCK_NB)
            flock(self.__lock_file_handle, LOCK_UN)
        except BlockingIOError:
            lock_status = True

        logger.debug(
            "Lock file at {} is {}locked".format(
                self.path, "not " if not lock_status else ""
            )
        )
        return lock_status

    __enter__ = acquire

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def __del__(self):
        if self.__lock_file_handle:
            self.__lock_file_handle.close()
