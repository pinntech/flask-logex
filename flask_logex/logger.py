"""
Sets up logging scheme for the project.

The flask application is passed in and logging is setup on the instance
that is passed.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
import os
import sys
from flask import request


''' Define the logging format '''
log_format = """
-------------------------------------------------------------------------------

[error_id]       %(error_id)s
[type]           %(levelname)s
[location]       %(pathname)s:%(lineno)d
[module]         %(module)s
[function]       %(funcName)s
[time]           %(asctime)s
[message]        %(message)s"""


def get_logger(log_name):
    return logging.getLogger(log_name)


def log_exception(log_name, error_id, message):
    """Override."""
    logger = get_logger(log_name)
    exc_info = sys.exc_info()
    if exc_info[1] is None:
        exc_info = message
    logger.error("""Path %s
    HTTP Method: %s
    Client IP Address: %s
    User Agent: %s
    User Platform: %s
    User Browser: %s
    User Browser Version: %s
    """ % (request.path,
           request.method,
           request.remote_addr,
           request.user_agent.string,
           request.user_agent.platform,
           request.user_agent.browser,
           request.user_agent.version
           ),
        exc_info=exc_info,
        extra={"error_id": error_id})


def configure_logging(application):
    """
    Configure logging on the flask application.

    Parameters
    ----------
    application : flask.Flask
        The Flask application instance.
    """
    # Log format
    application.debug_log_format = log_format
    # Environment determines log level
    environment = os.environ.get('ENVIRONMENT', 'local')
    if environment == 'local':
        LOG_LEVEL = logging.INFO
    elif environment == 'development':
        LOG_LEVEL = logging.WARNING
    else:
        LOG_LEVEL = logging.ERROR
    # Set application log level
    application.logger.setLevel(LOG_LEVEL)
