from pitop.core.exceptions import UnavailableComponent


class SupportsCamera:
    def __init__(self, camera_device_index, camera_resolution, **kwargs):
        try:
            from pitop.camera import Camera
            self._camera = Camera(camera_device_index, camera_resolution)
        except Exception:
            self._camera = None
            print("No camera")

    @property
    def camera(self):
        if self._camera:
            return self._camera
        raise UnavailableComponent("Camera not available")
