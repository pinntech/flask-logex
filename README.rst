===========
Flask-LogEx
===========

One stop shop for logging, exception handling, and consistent error responses.
Along with all that, LogEx enables a caching mechanism for tracing purposes.
Using trace_ids, you'll be able to diagnose issues throughout the stack trace.


Highlights
^^^^^^^^^^

* Protocol follows `werkzeug.exceptions.HTTPException <https://github.com/pallets/werkzeug/blob/master/werkzeug/exceptions.py>`_

* Exceptions are caught for Flask Apps, Blueprints, and Flask-Restful Apis.
  The goal is to have uniform responses for API's served by any Flask package.

  JSON Response bodies are consistent and follow this format 
  
  .. code-block:: json
  {
        "error": {
                        "message": "Error message!",
                        
                        "code": 500,
                        
                        "type": "server_error"
                 }
  }

* Dynamic creation of loggers_ attached to appliations, log files in designated log paths
  and customized formatting_. Log levels can be controlled with `ENVIRONMENT` env.
  
.. table:: Environment Settings
   :widths: auto
   :align: center
   
              ============= =========
              Environment   Level
              ============= =========
              `local`        `INFO`
              `development`  `WARNING`
              `staging`      `ERROR`
              `production`   `ERROR`
              ============= =========

* Default exception handling for HTTPException with ability to extend in handlers_ property.
  See `flask_logex.exceptions.handle_error`.

* Optionality to use a cache_ mechanism log traceback, trace ids will be able to be used to query
  request and responses that had a bug.

* `flask_logex.defaults
  <https://github.com/pinntech/flask-logex/blob/master/flask_logex/defaults.py>`_
  contains base values for everything discussed.
        * Boto integration with own handler and logger
        * Webargs Validation Error response handling is one to one with reqparse,
          the two most common Flask parsers
        * Log format with most verbosity
        * Log and trace codes specifies which error codes take action

.. contents::

Installation
------------

1. Clone the repository `git clone https://github.com/tcco/flask-logex.git`
2. Enter `cd flask-logex`
3. To develop `python setup.py develop`
4. To install `python setup.py install`
5. To test `pytest -s tests`

Pip Install

`pip install git+https://github.com/pinntech/flask-logex.git@__version__#egg=flask-logex`

Once we release `1.0.0`, we will publish to pip public repository


Usage
-----

Examples dicussed can be found within the repository at `tests/samples.py
<https://github.com/pinntech/flask-logex/blob/master/tests/samples.py>`_

Initialization
^^^^^^^^^^^^^^
Initialize without any customization ::

    from flask_logex import LogEx
    logex = LogEx()

    from flask import Flask
    from flask_restful import Api

    app = Flask(__name__)
    api = Api(app)
    logex.init_app(app, api)

Blueprints example ::

    from flask_logex import LogEx
    logex = LogEx()

    from flask import Flask, Blueprint
    from flask_restful import Api

    bp_v1 = Blueprint('v1', url_prefix='/v1')
    api_v1 = Api(bp_v1)
    bp_v2 = Blueprint('v2', url_prefix='/v2')
    api_v2 = Api(bp_v2)

    app = Flask(__name__)
    app.register_blueprint(bp_v1)
    app.register_blueprint(bp_v2)
    logex.init_app(app, [api_v1, api_v2])

.. _formatting:

Formatting
^^^^^^^^^^
Defaults are set in flask_logex.LogEx.log_format, refer to for example. For more on log
formats refer to `logrecord-attributes
<https://docs.python.org/3/library/logging.html#logrecord-attributes>`_ ::

    log_format = """%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"""
    log_format = logging.Formatter(log_format)
    logex = Logex(log_format=log_format)

.. _loggers:

Loggers
^^^^^^^
Set loggers property in logex before init_app. Using dict mapping exceptions to name
of logger retrieved from logging.getLogger(). Use the base class of the exceptions thrown,
ensuring all exceptions are caught and logged to the proper log file. Log files are
created and loggers are added to the application ::

    from boto.compat import StandardError
    loggers = {StandardError: "boto",
               CustomError: "custom"}

    logex = Logex(loggers=loggers)

.. _handlers:

Exceptions and Handlers
^^^^^^^^^^^^^^^^^^^^^^^
When initializing LogEx, utilize a dictionary that is keyed with the exception class
(recommend using base classes when possible) and valued with either the handler for that
class or None is no handle needed. By default, exceptions will be checked for a HTTPException
in `flask_logex.exceptions.handle_http_exception`.

`flask_logex.exceptions.AppException` is a provided custom exception that examples
how to write application specific errors. Ones that by HTTP protocol are `200` but error
due to application reasons, like a user's email being duplicated.

Here is an example of a LogEx initialization with an application error and a
custom boto error that has its own handler. Parameters include the exception and
the error response that will be overriden on keys `code`, `message`, and `type` ::

    from boto.compat import ServerError

    def handle_boto(e, error):
        error = {}
        if issubclass(e, ServerError):
            error["code"] = 500
            error["message"] = str(e.reason)
            error["type"] = "boto_exception"
        return error

    class UserEmailExists(AppException):
        error_type = 'user_email_exists'
        error_message = 'Email provided is already taken!'

    handlers = {StandardError: handle_boto,
                UserEmailExists: None}

    logex = Logex(handlers=handlers)

.. _cache:

Cache
^^^^^
Cache can be configured by either initializing at init or init_app with a dictionary
of configurations or set directly to the app.config at runtime. By default, cache is
not turned on so tracing is not enabled. Take a look at the differect `cache types
<http://werkzeug.pocoo.org/docs/0.12/contrib/cache/>`_. ::

  cache_config = {
                        "LOGEX_CACHE_TYPE": "redis",
                        "LOGEX_CACHE_REDIS_HOST": 'localhost',
                        "LOGEX_CACHE_DEFAULT_TIMEOUT": 0
                 }
  logex = Logex(cache_config=cache_config)


Contributing
------------

Want to contribute? Here's how you can help...

1. Fork it
2. Create your feature branch: git checkout -b my-new-feature
3. Test your changes with `py.test tests`
4. Commit your changes: git commit -am 'Add some feature'
5. Push to the branch: git push origin my-new-feature
6. Submit a pull request

License
-------

The MIT License (MIT)

Copyright (c) 2017 Pinn Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
