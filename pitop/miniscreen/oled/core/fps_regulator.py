from time import sleep
try:
    from time import monotonic
except ImportError:
    from monotonic import monotonic


class FPS_Regulator(object):
    """
    Adapted from ``luma.core.spritesheet``

    Implements a variable sleep mechanism to give the appearance of a consistent
    frame rate. Using a fixed-time sleep will cause animations to be jittery
    (looking like they are speeding up or slowing down, depending on what other
    work is occurring), whereas this class keeps track of when the last time the
    ``sleep()`` method was called, and calculates a sleep period to smooth out
    the jitter.
    :param fps: The max frame rate, expressed numerically in
        frames-per-second.  By default, this is set at 16.67, to give a frame
        render time of approximately 60ms. This can be overridden as necessary,
        and if no FPS limiting is required, the ``fps`` can be set to zero.
    :type fps: float
    """

    def __init__(self, max_fps=16.67):
        self.set_max_fps(max_fps)
        self.total_transit_time = 0
        self.start_time = None
        self.last_time = None
        self.fps = 30

    def set_max_fps(self, max_fps):
        """
        Sets the max frame rate to the value provided

        Parameters
        ----------
        max_fps : int
          The frame rate that the user aims to render to the screen at. Lower frame rates are permitted.
        """
        self.total_no_of_frames = 0
        if max_fps == 0:
            max_fps = -1
        self.max_sleep_time = 1.0 / max_fps

    def throttle_fps_if_needed(self):
        """
        Sleep to ensure that max frame rate is not exceeded
        """
        if self.max_sleep_time >= 0:
            last_frame_transit_time = monotonic() - self.last_time
            sleep_for = self.max_sleep_time - last_frame_transit_time

            if sleep_for > 0:
                sleep(sleep_for)

    def start_timer(self):
        """
        Starts internal timer so that time taken to render frame can be known
        """
        self.enter_time = monotonic()
        if not self.start_time:
            self.start_time = self.enter_time
            self.last_time = self.enter_time

    def stop_timer(self):
        """
        Stops internal timer so that time taken to render frame can be known. Responsible for throttling frame rate as
         required
        """
        try:
            self.total_transit_time += monotonic() - self.enter_time
            self.total_no_of_frames += 1
            self.throttle_fps_if_needed()

            self.last_time = monotonic()
        except AttributeError:
            pass

    def effective_FPS(self):
        """
        Calculates the effective frames-per-second - this should largely
        correlate to the max FPS supplied in the constructor, but no
        guarantees are given.
        :returns: the effective frame rate
        :rtype: float
        """
        if self.start_time is None:
            self.start_time = 0
        elapsed = monotonic() - self.start_time
        return self.total_no_of_frames / elapsed

    def average_transit_time(self):
        """
        Calculates the average transit time between the enter and exit methods,
        and return the time in milliseconds
        :returns: the average transit in milliseconds
        :rtype: float
        """
        return self.total_transit_time * 1000.0 / self.total_no_of_frames
