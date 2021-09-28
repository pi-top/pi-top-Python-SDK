from threading import Thread

from pyinotify import IN_CLOSE_WRITE, IN_OPEN, Notifier, ProcessEvent, WatchManager


class MiniscreenLockFileMonitor:
    def __init__(self, lock_path):
        self.thread = Thread(target=self._monitor_lockfile)
        self.when_user_stops_using_oled = None
        self.when_user_starts_using_oled = None
        self.lock_path = lock_path

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
        notifier = Notifier(wm, eh)
        notifier.loop()

    def start(self):
        self.stop()
        self.thread = Thread(target=self._monitor_lockfile)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(0)
