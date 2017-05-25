from boto.exception import JSONResponseError, DynamoDBResponseError
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


custom = [SampleException, JSONResponseError]
app = Flask(__name__)
api = Api(app)
logex = LogEx(app, api, custom)


@app.route('/app/sample')
def sample():
    raise SampleException('Route Test Error')


@app.route('/app/default')
def bad_request():
    raise BadRequest('Route Test Error')


@app.route('/app/boto')
def boto():
    raise DynamoDBResponseError(400, reason="Boto", body={"message": "message"})


class SampleExc(Resource):
    def get(self):
        raise SampleException('Resource Test Error')


class BadRequestExc(Resource):
    def get(self):
        raise BadRequest('Resource Test Error')


class BotoExc(Resource):
    def get(self):
        raise DynamoDBResponseError(400, reason="Boto", body={"message": "message"})


api.add_resource(BadRequestExc, '/api/default')
api.add_resource(SampleExc, '/api/sample')
api.add_resource(BotoExc, '/api/boto')
