import pickle
from io import BytesIO

import pytest
from imgcat import imgcat
from PIL import Image, ImageChops


def is_master(config):
    return not hasattr(config, "workerinput")


def pytest_configure(config):
    plugin = SnapshotReporter(config)
    config.pluginmanager.register(plugin)


class SnapshotReporter:
    def __init__(self, config):
        self.config = config
        self.is_master = is_master(config)
        self.failed_snapshots = []

    def track_snapshot(self, snapshot):
        def track_assert(fn):
            def tracked(value, snapshot_name):
                try:
                    fn(value, snapshot_name)
                except AssertionError as e:
                    path = snapshot._snapshot_path(snapshot_name)
                    self.failed_snapshots.append(
                        {
                            "path": str(path),
                            "received": value,
                            "expected": path.read_bytes() if path.is_file() else None,
                        }
                    )

                    raise e

            return tracked

        snapshot.assert_match = track_assert(snapshot.assert_match)
        snapshot.assert_match_dir = track_assert(snapshot.assert_match_dir)

    @pytest.fixture
    def snapshot(self, snapshot):
        self.track_snapshot(snapshot)
        yield snapshot

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        yield
        if not self.is_master:
            self.config.workeroutput["failed_snapshots"] = pickle.dumps(
                self.failed_snapshots
            )

    def pytest_testnodedown(self, node, error):
        worker_snapshots = pickle.loads(node.workeroutput["failed_snapshots"])
        self.failed_snapshots.extend(worker_snapshots)

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        if exitstatus == 0:
            return

        terminalreporter.write_sep("=", "snapshot diff")

        for failed_snapshot in self.failed_snapshots:
            terminalreporter.write_sep("-", failed_snapshot["path"])

            terminalreporter.write_line("Received:")
            if failed_snapshot["received"]:
                imgcat(failed_snapshot["received"])
            else:
                terminalreporter.write_line("None")

            terminalreporter.write_line("Expected:")
            if failed_snapshot["expected"]:
                imgcat(failed_snapshot["expected"])
            else:
                terminalreporter.write_line("None")

            if failed_snapshot["received"] and failed_snapshot["expected"]:
                try:
                    image_received = Image.open(BytesIO(failed_snapshot["received"]))
                    image_expected = Image.open(BytesIO(failed_snapshot["expected"]))
                    difference = ImageChops.difference(image_received, image_expected)

                    terminalreporter.write_line("Difference:")
                    imgcat(difference)
                except Exception:
                    pass
