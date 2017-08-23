"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

__version__ = '0.2.0'

# System
# ~~~~~~
import json
import logging
import os
import subprocess

# Dependency
# ~~~~~~~~~~
from flask import Flask
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
from logger import log_exception
from trace import Tracer

# Defaults
# ~~~~~~~~
from defaults import __log_format__
from defaults import __error_map__
from defaults import __trace_codes__
from defaults import __log_codes__
from defaults import __handlers__
from defaults import __loggers__


class LogEx():
    """LogEx Extension Class."""

    def __init__(self,
                 app=None,
                 api=None,
                 cache_config=None,
                 handlers=None,
                 loggers=None,
                 log_format=__log_format__,
                 log_codes=__log_codes__,
                 trace_codes=__trace_codes__):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Optional Flask application.
        api : flask_restful.Api or list
            Optional Flask-RESTful Api or list of Api's.
        cache : werkzeug.contrib.cache.BaseCache
            Optional trace cache
        handlers : dict
            Optional with default mapping exceptions to handlers.
        loggers : dict
            Optional with default mapping exceptions to names of loggers.
        log_format : logging.Formatter
            Optional logging format, defaulted is flask_logex.logger.log_format.
        log_codes : list
            List of codes which when encountered should trigger logging.
        trace_codes : list
            List of codes that set traces when encountered.
        """
        # Log
        self.log_format = log_format
        self.log_codes = log_codes
        self.loggers = loggers
        self.loggers.update(__loggers__)  # Default Loggers
        # Exception Handlers
        self.handlers = handlers
        self.handlers.update(__handlers__)  # Default Handlers
        # Trace
        self.cache_config = cache_config
        self.trace_codes = trace_codes
        # Application
        self.app = app
        self._api = api
        if self.app is not None:
            self.init_app(app, api, cache_config)

    def init_app(self, app, api=None, cache_config=None):
        """
        Initialize LogEx Instance.

        Parameters
        ----------
        app : flask.Flask
            Flask application.
        api : flask_restful.Api or list
            Optional Flask-RESTful Api or list of Api's.
        """
        self.app = app
        if api:
            self._api = api
        if cache_config:
            self.cache_config = cache_config
        self.init_cache(app, cache_config)
        self.init_settings()
        self.init_logs()
        self.configure_exceptions()

    def check_app(self):
        """App property check."""
        if self.app is None:
            raise AttributeError(
                "Logex is not initialized, run init_app"
            )
        if type(self.app) is not Flask:
            raise AttributeError(
                "App is not flask.Flask"
            )

    @property
    def api(self):
        """Override property to conver to list of flask_restful.Api."""
        if self._api is None:
            return self._api
        if type(self._api) is not list:
            self._api = [self._api]
        return self._api

    def init_settings(self):
        """Initialize settings from environment variables."""
        self.check_app()
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
        self.LOG_PATH = os.environ.get("LOG_PATH", "./logs/")
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.INFO)
        # Log Directory
        if not os.path.isdir(self.LOG_PATH):
            try:
                subprocess.call(
                    ['mkdir', '-p', self.LOG_PATH]
                )
            except:
                raise StandardError(
                    "Unable to make log directory at {}".format(self.LOG_PATH)
                )

    def init_logs(self):
        """Configure logging on the flask application."""
        self.check_app()
        # Environment controlled loggging level
        self.LOG_LEVEL = logging.INFO
        if self.ENVIRONMENT == 'development':
            self.LOG_LEVEL = logging.WARNING
        elif self.ENVIRONMENT == 'production':
            self.LOG_LEVEL = logging.ERROR

        self.logs = {}
        # Loggers
        loggers = self.loggers.values()
        loggers.append(self.app.logger_name)
        for log_name in loggers:
            logger = add_logger(log_name, self)
            self.logs[log_name] = logger

    def init_cache(self, app, cache_config):
        """Create the cache based on passed cache config values."""
        self.check_app()
        # Use app config by default, otherwise supply cache_config
        config = app.config.copy()
        if self.cache_config:
            config.update(self.cache_config)
        if cache_config:
            config.update(cache_config)

        # Required to initialize
        config.setdefault('CACHE_TYPE', 'null')
        # Memcached + Gaememcached
        config.setdefault('CACHE_MEMCACHED_SERVERS', None)
        config.setdefault('CACHE_KEY_PREFIX', '')
        # Simple + Filesystem
        config.setdefault('CACHE_DIR', None)
        config.setdefault('CACHE_THRESHOLD', 500)
        # Redis
        config.setdefault('CACHE_REDIS_HOST', None)
        config.setdefault('CACHE_REDIS_PORT', None)
        config.setdefault('CACHE_REDIS_URL', None)
        config.setdefault('CACHE_REDIS_DB', None)
        config.setdefault('CACHE_REDIS_PASSWORD', None)
        config.setdefault('CACHE_KEY_PREFIX', None)
        # Options
        config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        config.setdefault('CACHE_OPTIONS', None)
        config.setdefault('CACHE_ARGS', [])
        config.setdefault('CACHE_NO_NULL_WARNING', False)

        cache_import = config['CACHE_TYPE']
        if '.' not in cache_import:
            from . import caches
            try:
                cache_obj = getattr(caches, cache_import)
            except AttributeError:
                raise ImportError("%s is not a valid FlaskCache backend" % (
                                  import_me))  # NOQA
        else:
            cache_obj = import_string(import_me)  # NOQA

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
                ctx.logex_tracer = Tracer(
                    self.cache_obj(
                        self.app,
                        self.cache_config,
                        self.cache_args,
                        self.cache_options)
                )
            return ctx.logex_tracer

    def configure_exceptions(self):
        """Configure exception handler for Flask and Flask-Restful."""
        self.check_app()
        # Add LogEx process_response to after request
        self.app.after_request_funcs.setdefault(None, []).append(self.process_response)
        # Default exceptions provided by werkzeug
        for code in default_exceptions:
            self.app.errorhandler(code)(self.jsonify_error)
            # Register errorhandler for Blueprints
            if self.app.blueprints:
                for bp_name in self.app.blueprints:
                    bp = self.app.blueprints[bp_name]
                    bp.errorhandler(code)(self.jsonify_error)
        # Custom exceptions provided by handlers
        for err in self.handlers.keys():
            if issubclass(err, Exception):
                self.app.errorhandler(err)(self.jsonify_error)
        # Flask-RESTful handle_error override
        if self.api:
            for api in self.api:
                api.handle_error = self.jsonify_error

    def process_response(self, response):
        """Handler for the Flask response hook to add in request/response tracing"""
        # Check for successfulk, empty, and irrelevant responses
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
            # Trace creation and dump
            trace_id = self.tracer.set(request, response)
            response_data = json.loads(response.data)
            response_data['error']['id'] = trace_id
            response.data = json.dumps(response_data)

        if code in self.log_codes:
            _loggers = self.loggers.keys()
            exc_type = type(g._logex_exception)
            # Log in custom logger, otherwise app.logger
            if issubclass(exc_type, tuple(_loggers)):
                key = [i for i in _loggers if issubclass(exc_type, i)][0]
                logger_name = self.loggers[key]
                log_exception(logger_name, message, trace_id)
            else:
                log_exception(self.app.logger_name, message, trace_id)
        return response

    def handle_error(self, e):
        """Handle error defaulted values and runs through handlers."""
        g._logex_exception = e
        code = e.code if hasattr(e, "code") else 500
        message = str(e)
        error_type = __error_map__[code] if code in __error_map__ else "unknown_error"
        error = dict(
            code=code,
            message=message,
            type=error_type
        )
        # Default error handler
        http_error = handle_http_exception(e)
        for key, value in http_error.iteritems():
            error[key] = value
        # Run error through custom error handlers to override response
        if type(e) in self.handlers and self.handlers[type(e)]:
            error = self.handlers[type(e)](e)
        return error

    def jsonify_error(self, e):
        """Separate jsonify and handle_error."""
        error = self.handle_error(e)
        return jsonify(error=error), error["code"]
