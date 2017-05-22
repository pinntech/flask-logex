"""
Sets up logging scheme for the project.

The flask application is passed in and logging is setup on the instance
that is passed.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
from flask import request
from os.environ import get


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


def log_exception(self, exc_info, error_id=None):
    """Override."""
    self.logger.error("""Path %s
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
        extra={'error_id': error_id})


def configure_logging(application):
    """
    Configure logging on the flask application.

    Parameters
    ----------
    application : flask.Flask
        The Flask application instance.
    """
    application.debug_log_format = log_format

    environment = get('ENVIRONMENT', 'local')

    if environment == 'local':
        LOG_LEVEL = logging.INFO
    elif environment == 'development':
        LOG_LEVEL = logging.WARNING
    else:
        LOG_LEVEL = logging.ERROR

    ''' Sets the application logger level '''
    application.logger.setLevel(LOG_LEVEL)
