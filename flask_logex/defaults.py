"""
Default settings for Logex.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""
import logging
from logger import log_format
from werkzeug.exceptions import HTTPException

__log_format__ = logging.Formatter(log_format)
__trace_codes__ = [422, 500, 501, 502, 503]
__log_codes__ = [422, 500, 501, 502, 503]
__handlers__ = {}
__loggers__ = {}

#
# Custom Boto Logging + Exception Handler
#
try:
    from boto.compat import StandardError

    def handle_boto_error(e):
        """Custom boto error handler for when boto is used."""
        error = {}
        if issubclass(e, StandardError):
            error["code"] = 500
            error["type"] = "boto_error"
            error["message"] = "Boto exception caught!"
            if hasattr("reason", e):
                error["message"] = str(e.reason)
            if hasattr("message", e):
                error["message"] = str(e.message)
    # Add logger and exception handler to logex defaults
    __loggers__[StandardError] = "boto"
    __handlers__[StandardError] = handle_boto_error
except ImportError:
    pass

#
# Webargs + Marshmallow Logging + Exception Handling
#
try:
    from webargs.flaskparser import parser

    class ValidationError(HTTPException):
        """Validation excetion written specific to Flask-LogEx."""
        code = 400
        data = {}

        def __init__(self, e):
            self.data["message"] = e.message

    @parser.errorhandler
    def handle_validation_error(e):
        """Webargs validation handling."""
        raise ValidationError(e)
except ImportError:
    pass


# Combining Flask Status Codes and werkzeug.exceptions.default_exceptions
__error_map__ = {
    400: "bad_request",
    401: "unauthorized",
    402: "payment_required",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    407: "proxy_authentication_required",
    408: "request_timeout",
    409: "conflict",
    410: "gone",
    411: "length_required",
    412: "precondition_failed",
    413: "request_entity_too_large",
    414: "request_uri_too_large",
    415: "unsupported_media_type",
    416: "requested_range_not_satisfiable",
    417: "expectation_failed",
    418: "i_am_a_teapot",
    422: "request_failed",
    423: "locked",
    428: "precondition_required",
    429: "rate_limit_exceeded",
    431: "request_header_fields_too_large",
    451: "unavailable_for_legal_reasons",
    500: "internal_server_error",
    501: "not_implemented",
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout",
    505: "http_version_not_supported",
    511: "network_authentication_failed"
}
