from flask import Flask
from flask_logex import LogEx
from flask_logex.exceptions import AppException
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest

_description = "description"
_error_code = 422
_error_type = "test_error"
_error_message = "test_message"


class SampleException(AppException):
    error_type = _error_type
    error_message = _error_message


errors = [SampleException]
logex = LogEx(errors=errors)

app = Flask(__name__)
api = Api(app)
logex.init_app(app, api)


@app.route('/app/sample')
def sample():
    raise SampleException('Route Test Error')


@app.route('/app/default')
def bad_request():
    raise BadRequest('Route Test Error')


class SampleExc(Resource):
    def get(self):
        raise SampleException('Resource Test Error')


class BadRequestExc(Resource):
    def get(self):
        raise BadRequest('Resource Test Error')


api.add_resource(BadRequestExc, '/api/default')
api.add_resource(SampleExc, '/api/sample')
