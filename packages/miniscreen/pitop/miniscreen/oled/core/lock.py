from threading import Thread

from pyinotify import IN_CLOSE_WRITE, IN_OPEN, Notifier, ProcessEvent, WatchManager


class MiniscreenLockFileMonitor:
    def __init__(self, lock_path):
        self.thread = Thread(target=self._monitor_lockfile, daemon=True)
        self.when_user_stops_using_oled = None
        self.when_user_starts_using_oled = None
        self.lock_path = lock_path
        self.notifier = None

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.notifier:
            self.notifier.stop()

        if self.__thread.is_alive():
            self.__thread.join()

    def _monitor_lockfile(self):
        eh = ProcessEvent()
        events_to_watch = 0
        if self.when_user_stops_using_oled:
            eh.process_IN_CLOSE_WRITE = lambda event: self.when_user_stops_using_oled()
            events_to_watch = events_to_watch | IN_CLOSE_WRITE
        if self.when_user_starts_using_oled:
            eh.process_IN_OPEN = lambda event: self.when_user_starts_using_oled()
            events_to_watch = events_to_watch | IN_OPEN

        wm = WatchManager()
        wm.add_watch(self.lock_path, events_to_watch)
        self.notifier = Notifier(wm, eh)
        self.notifier.loop()

    def start(self):
        self.stop()
        self.thread = Thread(target=self._monitor_lockfile, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(0)
