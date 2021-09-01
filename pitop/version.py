__version__ = "N/A"

try:
    with open("version.txt", "r+") as f:
        # Reading form a file
        __version__ = f.read().strip()

except Exception:
    pass
