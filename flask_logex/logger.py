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
log_format = (
    '-' * 80 + '\n' +
    """
    [type]              %(levelname)s
    [location]          %(pathname)s:%(lineno)d
    [module.function]   %(module)s.%(funcName)s
    [time]              %(asctime)s
    %(message)s
    """ +
    '-' * 80
)


def _should_log_for(app, mode):
    policy = app.config['LOGGER_HANDLER_POLICY']
    if policy == mode or policy == 'always':
        return True
    return False


def get_logger(log_name):
    return logging.getLogger(log_name)


def add_logger(log_name, logex):
    """Add logger from logging.getLogger."""
    app = logex.app
    log_path = logex.LOG_PATH + log_name + ".log"
    logger = get_logger(log_name)

    if len(logger.handlers):
        del logger.handlers[:]

    class DebugHandler(logging.StreamHandler):
        def emit(self, record):
            if app.debug and _should_log_for(app, 'debug'):
                logging.StreamHandler.emit(self, record)

    logger.setLevel(logex.LOG_LEVEL)

    debug_handler = DebugHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logex.log_format)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logex.LOG_LEVEL)
    file_handler.setFormatter(logex.log_format)

    logger.addHandler(file_handler)
    logger.addHandler(debug_handler)
    return logger


def log_exception(log_name, message, trace_id):
    """Override."""
    logger = get_logger(log_name)
    exc_info = sys.exc_info()
    data = ("""[trace-id]          %s
    [message]           %s
    [request]
        Method/Path:    %s %s
        Client IP:      %s
        User Agent:     %s
        Platform:       %s
        Browser:        %s
        Version:        %s
    """ % (trace_id,
           message,
           request.method,
           request.path,
           request.remote_addr,
           request.user_agent.string,
           request.user_agent.platform,
           request.user_agent.browser,
           request.user_agent.version
           ))
    if exc_info[1] is None:
        logger.error(data)
    else:
        logger.error(data, exc_info=exc_info)
