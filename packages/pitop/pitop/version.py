__version__ = "N/A"
try:
    from importlib.metadata import version

    __version__ = version("pitop")
except ImportError:
    try:
        from pkg_resources import get_distribution

        __version__ = get_distribution("pitop").version
    except Exception:
        __version__ = "N/A"
except Exception:
    __version__ = "N/A"
