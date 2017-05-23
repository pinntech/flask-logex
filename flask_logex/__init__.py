"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import logging
from os import path
from os.environ import get
from exceptions import configure_exceptions
from flask import _app_ctx_stack as stack
from logger import configure_logger, log_format
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

    def __init__(self, app=None, api=None):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Optional Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        """
        self.app = app
        self.api = api
        if self.app is not None:
            self.init_app(app, api)

    def init_app(self, app, api=None):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        """
        self.app = app
        self.api = api
        configure_logger(app)
        configure_exceptions(app, api)
        self.init_settings()

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.app.config.set_default('LOG_PATH', get('LOG_PATH', './logs'))
        self.app.config.set_default('LOG_LEVEL', get('LOG_LEVEL', 'INFO'))
        self.app.config.set_default('LOG_LIST', self.loggers.values())

    def add_logger(self, logger, log_path):
        """Add logger from logging.getLogger."""
        _logger = logging.getlogger(logger)
        _logger.setLevel(self.levels[self.app.level])
        log_file_handler = logging.FileHandler(log_path)
        log_file_handler.setLevel(self.levels[self.app.level])
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
            ctx.logs = {}
            if not hasattr(ctx, 'logs'):
                if not path.isdir(self.app.config['LOG_PATH']):
                    call(['mkdir', '-p', self.app.config['LOG_PATH']])

                for log in self.app.config['LOG_LIST']:
                    log_path = self.app.config['LOG_PATH'] + '/' + log + '.log'
                    if not path.isfile(log_path):
                        call(['touch', log_path])
                    logger = self.add_logger(self.loggers[log], log_path)
                    ctx.logs[log] = logger
            return ctx.logs

    def __getattr__(self, name):
        """Override getter to focus on loggers."""
        if name in self.logs:
            return self.logs[name]
        raise AttributeError("No log handler for {}".format(name))
