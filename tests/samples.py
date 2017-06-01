from flask import Flask
from flask_logex import LogEx
from flask_logex.exceptions import AppException
from flask_logex.exceptions import errorhandler
from flask_logex.logger import log_exception
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest

_description = "description"
_error_code = 422
_error_type = "test_error"
_error_message = "test_message"
log_map = {'application': '__name__',
           'test_exception': 'test_exception'}
app = Flask(__name__)
api = Api(app)


@errorhandler
def handle_test(e, error):
    if isinstance(e, CustomException):
        error["code"] = e.code
        error["message"] = e.description
        if e.code >= 500:
            log_exception("test_exception", error["code"], error["message"])
    return error


class SampleException(AppException):
    error_type = _error_type
    error_message = _error_message


class CustomException(Exception):
    code = 500
    description = "Customizing handle error"


errors = [SampleException, CustomException]
logex = LogEx(errors=errors,
              log_map=log_map,
              handle_error=handle_test)
logex.init_app(app, api)


@app.route('/app/custom')
def custom():
    raise CustomException()


@app.route('/app/sample')
def sample():
    raise SampleException('Route Test Error')


@app.route('/app/default')
def bad_request():
    raise BadRequest('Route Test Error')


class CustomExc(Resource):
    def get(self):
        raise CustomException()


class SampleExc(Resource):
    def get(self):
        raise SampleException('Resource Test Error')


class BadRequestExc(Resource):
    def get(self):
        raise BadRequest('Resource Test Error')


api.add_resource(BadRequestExc, '/api/default')
api.add_resource(SampleExc, '/api/sample')
api.add_resource(CustomExc, '/api/custom')
