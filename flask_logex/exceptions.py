"""
Define all possible request exceptions of the API.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

from flask import jsonify
from uuid import uuid4
from werkzeug.exceptions import HTTPException
from logger import log_exception


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


def handle_error(e):
    """
    Handle for exceptions thrown and returns a Flask JSON reponse.

    Parameters
    ----------
    e : Exception
        An exception that is raised in the application.
    """
    code = 500
    message = str(e)
    error_id = uuid4()
    error_type = None
    param = None
    error = {"id": str(error_id)}

    # HTTP
    if isinstance(e, HTTPException):
        code = e.code
        message = e.error_message if hasattr(e, "error_message") else e.description
        # Reqparse error handling
        if hasattr(e, "data") and "message" in e.data:
            message = e.data["message"].values()[0]
            param = e.data["message"].keys()[0]
        if code >= 500 or code == 422:
            log_exception("__name__", error_id, message)

    # Custom
    error_type = e.error_type if hasattr(e, "error_type") else LOGEX_ERROR_MAP[code]

    # Error
    error["type"] = error_type
    error['message'] = message
    if param:
        error["param"] = param

    response = jsonify(error=error), code
    return jsonify(error=error), code


class AppException(HTTPException):
    """App exception with custom error type and messages."""

    code = 422
    error_type = None
    error_message = None

    def __init__(self, description=None, response=None):
        if self.error_type is None:
            assert AttributeError("error_type must be set")
        if self.error_message is None:
            assert AttributeError("error_message must be set")
        HTTPException.__init__(self, description, response)
