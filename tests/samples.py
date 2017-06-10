from flask import Flask
from flask_logex import LogEx
from flask_logex.exceptions import AppException
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest
from werkzeug.contrib.cache import SimpleCache

_description = "description"
_error_code = 422
_error_type = "test_error"
_error_message = "test_message"
app = Flask(__name__)
api = Api(app)


def handle_custom_exception(e):
    error = {}
    if isinstance(e, CustomException):
        error["code"] = e.code
        error["message"] = e.description
        error["type"] = e.error_type
    return error


class SampleException(AppException):
    error_type = _error_type
    error_message = _error_message


class CustomException(Exception):
    code = 500
    description = "Customizing handle error"
    error_type = "custom_exceeption"


handlers = {CustomException: handle_custom_exception,
            SampleException: None}
loggers = {CustomException: "custom_exception"}
try:
    from boto.exception import JSONResponseError
    from boto.exception import DynamoDBResponseError

    @app.route('/app/boto')
    def boto_route():
        raise DynamoDBResponseError(500, "reason")

    class BotoExc(Resource):
        def get(self):
            raise DynamoDBResponseError(500, "reason")

    def handle_boto_exception(e):
        error = dict(code=500,
                     message="boto_error",
                     type="boto_error")
        return error

    api.add_resource(BotoExc, '/api/boto')
    loggers[JSONResponseError] = "boto"
    handlers[JSONResponseError] = handle_boto_exception
except:
    pass

# cache = RedisCache()
cache = SimpleCache()
logex = LogEx(handlers=handlers,
              loggers=loggers,
              cache=cache)
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


@app.route('/app/ok')
def ok():
    from flask import jsonify
    return jsonify({})


@app.route('/app/none')
def none():
    from flask import jsonify
    return jsonify(None), 204


class CustomExc(Resource):
    def get(self):
        raise CustomException()


class SampleExc(Resource):
    def get(self):
        raise SampleException('Resource Test Error')


class BadRequestExc(Resource):
    def get(self):
        raise BadRequest('Resource Test Error')


class OkResource(Resource):
    def get(self):
        return {}, 200


class NoneResource(Resource):
    def get(self):
        return None, 204


api.add_resource(BadRequestExc, '/api/default')
api.add_resource(SampleExc, '/api/sample')
api.add_resource(CustomExc, '/api/custom')
api.add_resource(OkResource, '/api/ok')
api.add_resource(NoneResource, '/api/none')
