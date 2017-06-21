"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

__version__ = '0.1.6'

# System
# ~~~~~~
import json
import logging
import os
import subprocess

# Dependency
# ~~~~~~~~~~
from flask import g
from flask import jsonify
from flask import request
from flask import _app_ctx_stack as stack
from werkzeug.exceptions import *  # NOQA
from werkzeug.exceptions import default_exceptions

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
LOGEX_ERROR_MAP = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "request_failed",
    429: "rate_limit_exceeded",
    500: "internal_server_error",
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout"
}
LOGEX_TRACE_CODES = [422, 500, 501, 502, 503]
LOGEX_LOG_CODES = [422, 500, 501, 502, 503]
LOGEX_HANDLERS = {}
LOGEX_LOGGERS = {}


class LogEx():
    """LogEx Extension Class."""

    def __init__(self,
                 app=None,
                 api=None,
                 cache_config=None,
                 handlers=LOGEX_HANDLERS,
                 loggers=LOGEX_LOGGERS,
                 log_format=LOGEX_FORMAT,
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
            Optional exception handler dict, maps exceptions to handlers.
        loggers : dict
            Optional logging map, maps exceptions to names of loggers.
        log_format : logging.Formatter
            Optional logging format, defaulted is flask_logex.logger.log_format.
        log_codes : list
            List of codes which when encountered should trigger logging.
        trace_codes : list
            List of codes that set traces when encountered.
        """
        self.app = app
        self.api = api
        self.cache_config = cache_config
        self.handlers = handlers
        self.log_format = log_format
        self.loggers = loggers
        self.log_codes = log_codes
        self.trace_codes = trace_codes
        if self.app is not None:
            self.init_app(app, api, cache_config)

    def init_app(self, app, api=None, cache_config=None):
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
        if api:
            self.api = api
        if cache_config:
            self.cache_config = cache_config
        self.init_cache(app, cache_config)
        self.logs = {}
        self.init_settings()
        self.init_logs()
        self.configure_logging()
        self.configure_exceptions()

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
        self.APPLICATION_LOG = os.environ.get("APPLICATION_LOG", "application")
        self.LOG_PATH = os.environ.get("LOG_PATH", "./logs/")
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
        self.LOG_LIST = ["__name__"]
        self.LOG_LIST.extend(self.loggers.values())

    def init_logs(self):
        """Log files property."""
        # Log directory
        if not os.path.isdir(self.LOG_PATH):
            subprocess.call(['mkdir', '-p', self.LOG_PATH])
        # Loggers
        for log in self.LOG_LIST:
            log_file = self.APPLICATION_LOG if log == "__name__" else log
            path = self.LOG_PATH + log_file + '.log'
            logger = get_logger(log)
            add_logger(logger, path, self.LOG_LEVEL, self.log_format)
            self.logs[log_file] = logger

    def init_cache(self, app, cache_config):
        """Create the cache based on passed cache config values."""
        base_config = app.config.copy()
        if self.cache_config:
            base_config.update(self.cache_config)
        if cache_config:
            base_config.update(cache_config)
        config = base_config

        config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        config.setdefault('CACHE_THRESHOLD', 500)
        config.setdefault('CACHE_KEY_PREFIX', '')
        config.setdefault('CACHE_MEMCACHED_SERVERS', None)
        config.setdefault('CACHE_DIR', None)
        config.setdefault('CACHE_OPTIONS', None)
        config.setdefault('CACHE_ARGS', [])
        config.setdefault('CACHE_TYPE', 'null')
        config.setdefault('CACHE_NO_NULL_WARNING', False)

        cache_import = config['CACHE_TYPE']
        if '.' not in cache_import:
            from . import caches

            try:
                cache_obj = getattr(caches, cache_import)
            except AttributeError:
                raise ImportError("%s is not a valid FlaskCache backend" % (
                                  import_me))
        else:
            cache_obj = import_string(import_me)

        cache_args = config['CACHE_ARGS'][:]
        cache_options = {'default_timeout': config['CACHE_DEFAULT_TIMEOUT']}

        if config['CACHE_OPTIONS']:
            cache_options.update(config['CACHE_OPTIONS'])

        self.cache_config = config
        self.cache_args = cache_args
        self.cache_options = cache_options
        self.cache_obj = cache_obj

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'logex_tracer'):
            ctx.logex_tracer = None

    @property
    def tracer(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'logex_tracer'):
                ctx.logex_tracer = Tracer(self.cache_obj(self.app, self.cache_config, self.cache_args, self.cache_options))
            return ctx.logex_tracer

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
        if not hasattr(g, "_logex_exception"):
            return response

        trace_id = None
        code = response_data['error']['code']
        message = response_data['error']['message']

        if self.tracer and code in self.trace_codes:
            trace_id = self.tracer.set(request, response)
            response_data = json.loads(response.data)
            response_data['error']['id'] = trace_id
            response.data = json.dumps(response_data)

        if code in self.log_codes:
            _loggers = self.loggers.keys()
            exc_type = type(g._logex_exception)
            if issubclass(exc_type, tuple(_loggers)):
                key = [i for i in _loggers if issubclass(exc_type, i)][0]
                logger_name = self.loggers[key]
                log_exception(logger_name, message, trace_id)
            else:
                log_exception("__name__", message, trace_id)
        return response

    def handle_error(self, e):
        """Handle error defaulted values and runs through handlers."""
        g._logex_exception = e
        code = e.code if hasattr(e, "code") else 500
        message = str(e)
        error_type = LOGEX_ERROR_MAP[code]
        error = dict(
            code=code,
            message=message,
            type=error_type
        )
        http_error = handle_http_exception(e)
        for key, value in http_error.iteritems():
            error[key] = value

        if type(e) in self.handlers and self.handlers[type(e)]:
            error = self.handlers[type(e)](e)
        return error

    def jsonify_error(self, e):
        """Separate jsonify and handle_error."""
        error = self.handle_error(e)
        return jsonify(error=error), error["code"]
