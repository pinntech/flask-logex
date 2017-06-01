"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import json
import logging
import os
from subprocess import call
from flask import request
from werkzeug.exceptions import *  # NOQA
from werkzeug.exceptions import default_exceptions
from exceptions import handle_error
from logger import add_logger
from logger import get_logger
from logger import logex_format
from trace import Tracer


class LogEx():
    """LogEx Extension Class."""

    levels = {50: logging.CRITICAL,
              40: logging.ERROR,
              30: logging.WARNING,
              20: logging.INFO,
              10: logging.DEBUG,
              0: logging.NOTSET}

    def __init__(self,
                 app=None,
                 api=None,
                 errors=None,
                 log_format=None,
                 log_map=None,
                 cache=None,
                 process_response=None):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Optional Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        errors : list
            Optional list of custom HTTPExceptions specific to application.
        log_format : logging.Formatter
            Optional logging format, defaulted is in flask_logex.logger
        log_map : dict
            Optional logging map, maps log files to logging.Logger
        cache : werkzeug.contrib.cache.BaseCache
            Optional trace cache
        process_response : function
            Hook to override Flask process_response, function must take response as a required
            parameter and trace_id as an optional parameter.
        """
        self.app = app
        self.api = api
        self.errors = errors
        self.log_format = log_format
        self.log_map = log_map
        self.process_response = process_response
        if cache:
            self.tracer = Tracer(cache)
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

        if self.errors is None:
            self.errors = []
        if self.log_format is None:
            self.log_format = logex_format
        if self.log_map is None:
            self.log_map = {'application': '__name__'}

        self.logs = {}
        self.init_settings()
        self.init_logs()
        self.configure_logging()
        self.configure_exceptions()

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
        self.LOG_PATH = os.environ.get("LOG_PATH", "./logs/")
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
        self.LOG_LIST = self.log_map.keys()
        # Log file creation
        if not os.path.isdir(self.LOG_PATH):
            call(['mkdir', '-p', self.LOG_PATH])

        for log in self.LOG_LIST:
            path = self.LOG_PATH + log + '.log'
            if not os.path.isfile(path):
                call(['touch', path])
            self.logs[log] = path

    def init_logs(self):
        """Log files property."""
        for (log, log_path) in self.logs.iteritems():
            log_name = self.log_map[log]
            logger = get_logger(log_name)
            add_logger(logger, log_path, self.LOG_LEVEL, self.log_format)
            self.logs[log] = logger

    def configure_logging(self):
        """Configure logging on the flask application."""
        if self.app is None:
            raise AttributeError("Logex is not initialized, run init_app")
        # Log format
        self.app.debug_log_format = self.log_format
        if self.ENVIRONMENT == 'local':
            LOG_LEVEL = logging.INFO
        elif self.ENVIRONMENT == 'development':
            LOG_LEVEL = logging.WARNING
        else:
            LOG_LEVEL = logging.ERROR
        # Set application log level
        self.app.logger.setLevel(LOG_LEVEL)

    def configure_exceptions(self):
        """Configure exception handler for Flask and Flask-Restful."""
        if self.app is None:
            raise AttributeError("Logex is not initialized, run init_app")
        # Default exceptions provided by werkzeug
        for code in default_exceptions:
            self.app.errorhandler(code)(handle_error)
        # Custom application errors
        for err in self.errors:
            self.app.errorhandler(err)(handle_error)
        # Flask-RESTful handle_error override
        if self.api:
            self.api.handle_error = handle_error
        self.app.process_response = self._process_response

    def _process_response(self, response):
        """Handler for the Flask response hook to add in request/response tracing"""
        if self.tracer:
            trace_id = self.tracer.set(request, response)
            response_data = json.loads(response.data)
            response_data['error']['id'] = trace_id
            response.data = json.dumps(response_data)
        if self.process_response:
            self.process_response(response, trace_id)
        return response
