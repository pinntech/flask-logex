from flask import Flask, Blueprint
from flask_logex import LogEx
from flask_logex.exceptions import AppException
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest

app = Flask("app")
# app.config["DEBUG"] = True
api = Api(app)

bp1 = Blueprint('v1', import_name='v1', url_prefix='/v1')
bp2 = Blueprint('v2', import_name='v2', url_prefix='/v2')
api_v1 = Api(bp1)
api_v2 = Api(bp2)


# Exceptions
class SampleException(AppException):  # NOQA
    error_type = "test_error"
    error_message = "test_message"


class CustomException(Exception):
    code = 500
    description = "Customizing handle error"
    error_type = "custom_exception"


# Routes and Resources
@app.route('/app/ok')  # NOQA
@bp1.route('/app/ok')
@bp2.route('/app/ok')
def ok():
    from flask import jsonify
    return jsonify({})


@app.route('/app/none')
@bp1.route('/app/none')
@bp2.route('/app/none')
def none():
    from flask import jsonify
    return jsonify(None), 204


@app.route('/app/custom')
@bp1.route('/app/custom')
@bp2.route('/app/custom')
def custom():
    raise CustomException()


@app.route('/app/sample')
@bp1.route('/app/sample')
@bp2.route('/app/sample')
def sample():
    raise SampleException('Route Test Error')


@app.route('/app/bad')
@bp1.route('/app/bad')
@bp2.route('/app/bad')
def bad_request():
    raise BadRequest('Route Test Error')


@app.route('/app/error')
@bp1.route('/app/error')
@bp2.route('/app/error')
def error():
    print hello  # NOQA


class OkResource(Resource):
    def get(self):
        return {}, 200


class NoneResource(Resource):
    def get(self):
        return None, 204


class CustomResource(Resource):
    def get(self):
        raise CustomException()


class SampleResource(Resource):
    def get(self):
        raise SampleException('Resource Test Error')


class BadResource(Resource):
    def get(self):
        raise BadRequest('Resource Test Error')


class ErrorResource(Resource):
    def get(self):
        print hello  # NOQA


try:
    from boto.exception import DynamoDBResponseError

    @app.route('/app/boto')
    @bp1.route('/app/boto')
    @bp2.route('/app/boto')
    def boto_route():
        raise DynamoDBResponseError(500, "reason")

    class BotoResource(Resource):
        def get(self):
            raise DynamoDBResponseError(500, "reason")

    api.add_resource(BotoResource, '/api/boto')
    api_v1.add_resource(BotoResource, '/api/boto')
    api_v2.add_resource(BotoResource, '/api/boto')
except:
    pass

try:
    from flask import request
    from webargs import fields
    from webargs.flaskparser import parser
    sample_args = {
        "hello": fields.Str(required=True),
        "world": fields.Str(required=True)
    }

    @app.route('/app/webargs')
    @bp1.route('/app/webargs')
    @bp2.route('/app/webargs')
    def webargs_route():
        args = parser.parse(sample_args)  # NOQA
        return args

    class WebArgsExc(Resource):
        def get(self):
            args = parser.parse(sample_args, request)  # NOQA

    api.add_resource(WebArgsExc, '/api/webargs')
    api_v1.add_resource(WebArgsExc, '/api/webargs')
    api_v2.add_resource(WebArgsExc, '/api/webargs')
except ImportError as e:
    print "Unable to import ValidationError"
    pass

# Classic Api Resource
api.add_resource(OkResource, '/api/ok')
api.add_resource(NoneResource, '/api/none')
api.add_resource(BadResource, '/api/bad')
api.add_resource(SampleResource, '/api/sample')
api.add_resource(CustomResource, '/api/custom')
api.add_resource(ErrorResource, '/api/error')
# Blueprint v1
api_v1.add_resource(OkResource, '/api/ok')
api_v1.add_resource(NoneResource, '/api/none')
api_v1.add_resource(BadResource, '/api/bad')
api_v1.add_resource(SampleResource, '/api/sample')
api_v1.add_resource(CustomResource, '/api/custom')
api_v1.add_resource(ErrorResource, '/api/error')
# Blueprint v2
api_v2.add_resource(OkResource, '/api/ok')
api_v2.add_resource(NoneResource, '/api/none')
api_v2.add_resource(BadResource, '/api/bad')
api_v2.add_resource(SampleResource, '/api/sample')
api_v2.add_resource(CustomResource, '/api/custom')
api_v2.add_resource(ErrorResource, '/api/error')

# Handlers
def handle_custom_exception(e):  # NOQA
    error = {}
    if isinstance(e, CustomException):
        error["code"] = e.code
        error["message"] = e.description
        error["type"] = e.error_type
    return error


# Logex
handlers = {  # NOQA
    CustomException: handle_custom_exception,
    SampleException: None
}
loggers = {
    CustomException: "custom_exception"
}
cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_DEFAULT_TIMEOUT': 300
}


logex = LogEx(
    app=app,
    api=api,
    handlers=handlers,
    loggers=loggers
)

bp_app = Flask("bp_app")
# bp_app.config["DEBUG"] = True
bp_app.register_blueprint(bp1)
bp_app.register_blueprint(bp2)
bp_logex = LogEx(
    app=bp_app,
    api=[api_v1, api_v2],
    handlers=handlers,
    loggers=loggers
)
