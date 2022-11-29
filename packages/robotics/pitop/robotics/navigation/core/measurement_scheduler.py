import sched
import time
from threading import Event, Thread


class MeasurementScheduler:
    def __init__(
        self, measurement_frequency, measurement_input_function, state_tracker
    ):
        if not callable(measurement_input_function):
            raise AttributeError(
                "Argument 'measurement_input_function' must be a function"
            )

        self.measurement_func = measurement_input_function
        self.state_tracker = state_tracker
        self._measurement_dt = 1.0 / measurement_frequency

        self._continue_processing = True
        self._new_measurement_event = Event()
        self._measurement_prediction_scheduler = Thread(target=self.start, daemon=True)
        self._measurement_prediction_scheduler.start()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._continue_processing = False
        if self._measurement_prediction_scheduler.is_alive():
            self._measurement_prediction_scheduler.join()

    def wait_for_measurement(self):
        self._new_measurement_event.wait()

    def start(self):
        s = sched.scheduler(time.time, time.sleep)
        current_time = time.time()
        s.enterabs(
            current_time + self._measurement_dt,
            1,
            self.loop,
            (s, current_time),
        )
        s.run()

    def loop(self, s, previous_time):
        current_time = time.time()
        self.state_tracker.add_measurements(
            odom_measurements=self.measurement_func(), dt=current_time - previous_time
        )

        self._new_measurement_event.set()
        self._new_measurement_event.clear()

        if self._continue_processing:
            s.enterabs(
                current_time + self._measurement_dt,
                1,
                self.loop,
                (s, current_time),
            )
