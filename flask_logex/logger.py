"""
Sets up logging scheme for the project.

The flask application is passed in and logging is setup on the instance
that is passed.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
import sys
from flask import request


''' Define the logging format '''
log_format = """
-------------------------------------------------------------------------------

[type]           %(levelname)s
[location]       %(pathname)s:%(lineno)d
[module]         %(module)s
[function]       %(funcName)s
[time]           %(asctime)s
[message]        %(message)s"""

LOGEX_FORMAT = logging.Formatter(log_format)


def add_logger(logger, log_path, log_level, log_format):
    """Add logger from logging.getLogger."""
    logger.setLevel(log_level)
    log_file_handler = logging.FileHandler(log_path)
    log_file_handler.setLevel(log_level)
    log_file_handler.setFormatter(log_format)
    logger.addHandler(log_file_handler)


def get_logger(log_name):
    return logging.getLogger(log_name)


def log_exception(log_name, message, trace_id):
    """Override."""
    logger = get_logger(log_name)
    exc_info = sys.exc_info()
    if exc_info[1] is None:
        exc_info = message
    data = ("""Trace-Id: %s
    Path: %s
    HTTP Method: %s
    Client IP Address: %s
    User Agent: %s
    User Platform: %s
    User Browser: %s
    User Browser Version: %s
    """ % (trace_id,
           request.path,
           request.method,
           request.remote_addr,
           request.user_agent.string,
           request.user_agent.platform,
           request.user_agent.browser,
           request.user_agent.version
           ))
    logger.error(
        data,
        exc_info=exc_info)
