"""
Contains configuration options for local, development, staging and production.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import os
import logging
from flask import Flask, request
from exceptions import handle_error
from logger import log_format, add_logger


class LogErr(Flask):
    """Override log_exception."""

    def __init__(self, app=None, api=None):
        """
        Initialize LogErr Instance.

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
        Initialize LogErr Instance.

        Parameters
        ----------
        app : flask.Flask
            Flask application.
        api : flask_restful.Api
            Optional Flask-RESTful Api.
        """
        self.app = app
        self.app.handle_http_exception = handle_error
        self.configure_logger(self.app)
        if api:
            self.api.handle_error = handle_error

    def log_exception(self, exc_info, error_id=None):
        """Override."""
        self.logger.error("""Path %s
        HTTP Method: %s
        Client IP Address: %s
        User Agent: %s
        User Platform: %s
        User Browser: %s
        User Browser Version: %s
        """ % (request.path,
               request.method,
               request.remote_addr,
               request.user_agent.string,
               request.user_agent.platform,
               request.user_agent.browser,
               request.user_agent.version
               ),
            exc_info=exc_info,
            extra={'error_id': error_id})

    def configure_logger(self, application):
        """
        Configure logginer on Flask application.

        Parameters
        ----------
        application : flask.Flask
            Flask applciation instance.
        """
        application.debug_log_format = log_format
        # Environment
        environment = os.environ.get('ENVIRONMENT', 'local')

        LOG_LEVEL = logging.INFO
        if environment == 'development':
            LOG_LEVEL = logging.WARNING
        if environment == 'staging':
            LOG_LEVEL = logging.ERROR
        if environment == 'production':
            LOG_LEVEL = logging.CRITICAL

        application.logger.setLevel(LOG_LEVEL)
