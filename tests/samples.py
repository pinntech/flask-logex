from flask import Flask, Blueprint
from flask_logex import LogEx
from flask_logex.exceptions import AppException
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest

app = Flask("app")
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


@app.route('/app/default')
@bp1.route('/app/default')
@bp2.route('/app/default')
def bad_request():
    raise BadRequest('Route Test Error')


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


try:
    from boto.exception import JSONResponseError
    from boto.exception import DynamoDBResponseError

    @app.route('/app/boto')
    @bp1.route('/app/boto')
    @bp2.route('/app/boto')
    def boto_route():
        raise DynamoDBResponseError(500, "reason")

    class BotoExc(Resource):
        def get(self):
            raise DynamoDBResponseError(500, "reason")

    api.add_resource(BotoExc, '/api/boto')
    api_v1.add_resource(BotoExc, '/api/boto')
    api_v2.add_resource(BotoExc, '/api/boto')
except:
    pass

# Classic Api Resource
api.add_resource(OkResource, '/api/ok')
api.add_resource(NoneResource, '/api/none')
api.add_resource(BadResource, '/api/default')
api.add_resource(SampleResource, '/api/sample')
api.add_resource(CustomResource, '/api/custom')
# Blueprint v1
api_v1.add_resource(OkResource, '/api/ok')
api_v1.add_resource(NoneResource, '/api/none')
api_v1.add_resource(BadResource, '/api/default')
api_v1.add_resource(SampleResource, '/api/sample')
api_v1.add_resource(CustomResource, '/api/custom')
# Blueprint v2
api_v2.add_resource(OkResource, '/api/ok')
api_v2.add_resource(NoneResource, '/api/none')
api_v2.add_resource(BadResource, '/api/default')
api_v2.add_resource(SampleResource, '/api/sample')
api_v2.add_resource(CustomResource, '/api/custom')

# Handlers
def handle_custom_exception(e):  # NOQA
    error = {}
    if isinstance(e, CustomException):
        error["code"] = e.code
        error["message"] = e.description
        error["type"] = e.error_type
    return error


def handle_boto_exception(e):
    error = dict(code=500,
                 message="boto_error",
                 type="boto_error")
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
    'CACHE_REDIS_HOST': 'ec2-54-67-77-214.us-west-1.compute.amazonaws.com',
    'CACHE_DEFAULT_TIMEOUT': 300
}
try:
    # Adding boto loggers and handlers if able to import
    import boto  # NOQA
    loggers[JSONResponseError] = "boto"
    handlers[JSONResponseError] = handle_boto_exception
except:
    pass

print "Classic Logex"
logex = LogEx(
    app=app,
    api=api,
    handlers=handlers,
    loggers=loggers,
    cache_config=None
)
print "Blue prints config with Logex"
bp_app = Flask("bp_app")
bp_app.register_blueprint(bp1)
bp_app.register_blueprint(bp2)
bp_logex = LogEx(
    app=bp_app,
    api=bp1,
    handlers=handlers,
    loggers=loggers,
    cache_config=None
)
