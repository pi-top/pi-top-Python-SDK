def _logger(cls):
    """Creates a logger with a name suitable for a specific class.

    This function takes into account that implementations for classes
    reside in platform dependent modules, and thus removes the final
    part of the module name.

    :param type cls: The class for which to create a logger.
    :return: a logger
    """
    import logging

    return logging.getLogger(
        "{}.{}".format(".".join(cls.__module__.split(".", 2)[:2]), cls.__name__)
    )
