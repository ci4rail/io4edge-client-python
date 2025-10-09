import logging

#
# We follow the recommendations from https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
#
# By default, if the application does not configure logging, the logging module will log
# only messages with level WARNING or above and is using the default formatting, i.e.
# only the message is printed.
#
# To get a more verbose output, the application should call, for example
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def io4edge_client_logger(name: str) -> logging.Logger:
    """
    Create a logger with the name 'io4edge-client:name'

    Returns
    -------
    logging.Logger
        The logger object.

    Parameters
    ----------
    name
        The name of the module, class or object that is using the logger.
    """
    return logging.getLogger("io4edge-client:" + name)
