"""
Sets up logging scheme for the project.

The flask application is passed in and logging is setup on the instance
that is passed.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import os
import logging


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


def configure_logging(application):
    """
    Configure logging on the flask application.

    Parameters
    ----------
    application : flask.Flask
        The Flask application instance.
    """
    application.debug_log_format = log_format

    environment = os.environ['ENVIRONMENT']

    LOG_LEVEL = logging.ERROR
    if environment == 'local':
        LOG_LEVEL = logging.INFO
    elif environment == 'development':
        LOG_LEVEL = logging.WARNING

    ''' Sets the application logger level '''
    application.logger.setLevel(LOG_LEVEL)

    log_directory = os.environ['LOG_PATH']

    ''' Application log '''
    application_log_file_handler = logging.FileHandler(
        log_directory + 'application.log'
    )
    application_log_file_handler.setFormatter(logging.Formatter(log_format))
    application.logger.addHandler(application_log_file_handler)

    ''' Dynamo log '''
    dynamo_logger = logging.getLogger('boto')
    dynamo_logger.setLevel(logging.INFO)
    dynamo_log_file_handler = logging.FileHandler(
        log_directory + 'dynamo.log')
    dynamo_log_file_handler.setLevel(logging.INFO)
    dynamo_log_file_handler.setFormatter(logging.Formatter(log_format))
    dynamo_logger.addHandler(dynamo_log_file_handler)


def add_logger(application):
    """
    Add logger and exception handler for log file.

    Parameters
    ----------
    application : flask.Flask
        The Flask application instance.
    """
    application.debug_log_format = log_format

    environment = os.environ['ENVIRONMENT']

    LOG_LEVEL = logging.ERROR
    if environment == 'local':
        LOG_LEVEL = logging.INFO
    elif environment == 'development':
        LOG_LEVEL = logging.WARNING

    ''' Sets the application logger level '''
    application.logger.setLevel(LOG_LEVEL)

    log_directory = os.environ['LOG_PATH']

    ''' Application log '''
    application_log_file_handler = logging.FileHandler(
        log_directory + 'application.log'
    )
    application_log_file_handler.setFormatter(logging.Formatter(log_format))
    application.logger.addHandler(application_log_file_handler)
