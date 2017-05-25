"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
import os
from exceptions import configure_exceptions
from exceptions import *  # NOQA
from flask import _app_ctx_stack as stack
from logger import configure_logging, log_format
from subprocess import call


class LogEx():
    """LogEx Extension Class."""

    log_format = log_format
    loggers = {'application': 'application',
               'dynamo': 'boto'}
    levels = {50: logging.CRITICAL,
              40: logging.ERROR,
              30: logging.WARNING,
              20: logging.INFO,
              10: logging.DEBUG,
              0: logging.NOTSET}

    def __init__(self, app=None, api=None, custom=[]):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Optional Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        custom : list
            Optional list of custom exceptions specific to application.
        """
        self.app = app
        self.api = api
        self.custom = custom
        if self.app is not None:
            self.init_app(app, api, custom)

    def init_app(self, app, api=None, custom=[]):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        custom : list
            Optional list of custom exceptions specific to application.
        """
        self.app = app
        self.api = api
        self.custom = custom
        configure_logging(app)
        configure_exceptions(app, api, custom)
        self.init_settings()

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.app.config.setdefault('LOG_PATH', os.environ.get('LOG_PATH', './logs/'))
        self.app.config.setdefault('LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO'))
        self.app.config.setdefault('LOG_LIST', self.loggers.keys())

    def add_logger(self, logger, log_path):
        """Add logger from logging.getLogger."""
        _logger = logging.getLogger(logger)
        level = self.levels[self.app.logger.level]
        _logger.setLevel(level)
        log_file_handler = logging.FileHandler(log_path)
        log_file_handler.setLevel(level)
        log_file_handler.setFormatter(logging.Formatter(self.log_format))
        _logger.addHandler(log_file_handler)
        return _logger

    @property
    def logs(self):
        """Log files property."""
        if self.app is None:
            raise AttributeError("Logex is not initialized, run init_app")
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'logs'):
                ctx.logs = {}
                log_path = self.app.config['LOG_PATH']
                log_list = self.app.config['LOG_LIST']
                if not os.path.isdir(log_path):
                    call(['mkdir', '-p', log_path])

                for log in log_list:
                    path = log_path + log + '.log'
                    if not os.path.isfile(path):
                        call(['touch', path])
                    logger = self.add_logger(self.loggers[log], path)
                    ctx.logs[log] = logger
            return ctx.logs
