"""
Define all possible request exceptions of the API.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

from werkzeug.exceptions import HTTPException


def handle_http_exception(e):
    """
    Handle for HTTPException.

    Defaulted in Flask-LogEx error handlers.
    Built to handle AppException below, looking
    for custom properties such as error_message
    and error_type.

    Parameters
    ----------
    e : Exception
        An exception that is raised in the application.

    Returns
    -------
    dict
        Error dictionary containining `code`, `message`, & `type`
    """
    error = {}
    if isinstance(e, HTTPException):
        error["code"] = e.code
        error["message"] = e.description
        # Reqparse & Marshmallow error handling
        if hasattr(e, "data") and "message" in e.data:
            error["message"] = e.data["message"].values()[0]
            error["param"] = e.data["message"].keys()[0]
        # Specific to AppException
        if hasattr(e, "error_type"):
            error["type"] = e.error_type
        if hasattr(e, "error_message"):
            error['message'] = e.error_message
    return error


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
