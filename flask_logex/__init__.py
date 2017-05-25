"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
import os
from exceptions import configure_exceptions
from exceptions import *  # NOQA
from logger import configure_logging, get_logger, log_format
from subprocess import call


class LogEx():
    """LogEx Extension Class."""

    log_format = log_format
    loggers = {'application': '__name__'}
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
        self.init_settings()
        configure_logging(app)
        configure_exceptions(app, api, custom)
        self.logs = self.init_logs()

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.LOG_PATH = os.environ.get("LOG_PATH", "./logs/")
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
        self.LOG_LIST = self.loggers.keys()

    def add_logger(self, logger, log_path):
        """Add logger from logging.getLogger."""
        level = self.levels[self.app.logger.level]
        logger.setLevel(level)
        log_file_handler = logging.FileHandler(log_path)
        log_file_handler.setLevel(level)
        log_file_handler.setFormatter(logging.Formatter(self.log_format))
        logger.addHandler(log_file_handler)

    def init_logs(self):
        """Log files property."""
        if self.app is None:
            raise AttributeError("Logex is not initialized, run init_app")
        logs = {}
        if not os.path.isdir(self.LOG_PATH):
            call(['mkdir', '-p', self.LOG_PATH])

        for log in self.LOG_LIST:
            path = self.LOG_PATH + log + '.log'
            if not os.path.isfile(path):
                call(['touch', path])
            logger = get_logger(self.loggers[log])
            self.add_logger(logger, path)
            logs[log] = logger
        return logs
