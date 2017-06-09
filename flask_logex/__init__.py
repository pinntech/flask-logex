"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

# System
# ~~~~~~
import json
import logging
import os
import subprocess
# Dependency
# ~~~~~~~~~~
from flask import jsonify
from flask import request
from werkzeug.exceptions import *  # NOQA
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
# Module Extension
# ~~~~~~~~~~~~~~~~
from exceptions import handle_http_exception
from logger import add_logger
from logger import get_logger
from logger import log_exception
from trace import Tracer


# Defaults
# ~~~~~~~~
from logger import LOGEX_FORMAT
LOGEX_MAP = {
    'application': '__name__'
}
LOGEX_ERROR_MAP = {
    400: "bad_request",
    401: "unauthorized",
    404: "method_not_allowed",
    409: "conflict",
    422: "request_failed",
    500: "internal_server_error",
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout"
}
LOGEX_TRACE_CODES = [422, 500, 501, 502, 503]
LOGEX_LOG_CODES = [422, 500, 501, 502, 503]
LOGEX_HANDLERS = {
    HTTPException: handle_http_exception
}


class LogEx():
    """LogEx Extension Class."""

    def __init__(self,
                 app=None,
                 api=None,
                 cache=None,
                 handlers=LOGEX_HANDLERS,
                 log_format=LOGEX_FORMAT,
                 log_map=LOGEX_MAP,
                 log_codes=LOGEX_LOG_CODES,
                 trace_codes=LOGEX_TRACE_CODES,):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Optional Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        cache : werkzeug.contrib.cache.BaseCache
            Optional trace cache
        handlers : dict
            Optional dict with methods handling keyed exception.
        log_format : logging.Formatter
            Optional logging format, defaulted is in flask_logex.logger
        log_map : dict
            Optional logging map, maps log files to logging.Logger
        log_codes : list
            List of codes which when encountered should trigger logging
        trace_codes : list
            List of codes that set traces when encountered
        """
        self.app = app
        self.api = api
        self.handlers = handlers
        self.log_format = log_format
        self.log_map = log_map
        self.log_codes = log_codes
        self.trace_codes = trace_codes
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
            subprocess.call(['mkdir', '-p', self.LOG_PATH])

        for log in self.LOG_LIST:
            path = self.LOG_PATH + log + '.log'
            if not os.path.isfile(path):
                subprocess.call(['touch', path])
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
            self.app.errorhandler(code)(self.jsonify_error)
        # Custom exceptions provided by handlers
        for err in self.handlers.keys():
            if issubclass(err, Exception):
                self.app.errorhandler(err)(self.jsonify_error)
        # Flask-RESTful handle_error override
        if self.api:
            self.api.handle_error = self.jsonify_error
        # Add LogEx process_response to after request
        self.app.after_request_funcs.setdefault(None, []).append(self.process_response)

    def process_response(self, response):
        """Handler for the Flask response hook to add in request/response tracing"""
        try:
            response_data = json.loads(response.data)
        except:
            return response
        if not response_data:
            return response
        if 'error' not in response_data:
            return response

        code = response_data['error']['code']
        message = response_data['error']['message']
        if self.tracer:
            if code in self.trace_codes:
                trace_id = self.tracer.set(request, response)
                response_data = json.loads(response.data)
                response_data['error']['id'] = trace_id
                response.data = json.dumps(response_data)

        if code in self.log_codes:
            log_exception("__name__", message, trace_id)

        return response

    def handle_error(self, e):
        """Handle error defaulted values and runs through handlers."""
        code = 500
        message = str(e)
        error_type = LOGEX_ERROR_MAP[code]
        error = dict(
            code=code,
            message=message,
            type=error_type
        )
        error = handle_http_exception(e, error)
        if type(e) in self.handlers:
            func = self.handlers[type(e)]
            if func:
                error = func(e)
        return error

    def jsonify_error(self, e):
        """Separate jsonify and handle_error."""
        error = self.handle_error(e)
        return jsonify(error=error), error["code"]
