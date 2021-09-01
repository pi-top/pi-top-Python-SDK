import os

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = "N/A"
try:
    with open(f"{HERE}/version.txt", "r+") as f:
        # Reading form a file
        __version__ = f.read().strip()

except Exception:
    pass
