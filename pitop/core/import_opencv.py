def import_opencv():
    try:
        import cv2

        return cv2
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "OpenCV Python library is not installed. You can install it by running 'sudo apt install python3-opencv libatlas-base-dev'."
        ) from None
