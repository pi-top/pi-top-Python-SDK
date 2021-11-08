import sched
import time
from threading import Event, Thread


class MeasurementScheduler:
    def __init__(self, measurement_frequency, odometry_function, state_tracker):
        self.state_tracker = state_tracker
        self.odometry_func = odometry_function
        self._measurement_dt = 1.0 / measurement_frequency

        self._pose_prediction_scheduler = Thread(
            target=self.__measurement_scheduler, daemon=True
        )
        self._new_pose_event = Event()

    def start(self):
        self._pose_prediction_scheduler.start()

    def wait_for_measurement(self):
        self._new_pose_event.wait()

    def __measurement_scheduler(self):
        s = sched.scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(
            current_time + self._measurement_dt,
            1,
            self.__measurement_loop,
            (s, current_time),
        )
        s.run()

    def __measurement_loop(self, s, previous_time):
        current_time = time.time()
        self.state_tracker.add_measurements(
            odom_measurements=self.odometry_func(), dt=current_time - previous_time
        )

        self._new_pose_event.set()
        self._new_pose_event.clear()

        s.enterabs(
            current_time + self._measurement_dt,
            1,
            self.__measurement_loop,
            (s, current_time),
        )
