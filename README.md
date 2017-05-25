# flask-logex
Flask Logging and Error Exception Extension

LogEx combines makes error handling, exception catching, and logging
accessible and customizable. This package allows for trace id within
logs easy to follow and diagnose issues with application. Integrate
a Flask application utilizing Flask-RESTful seamlessly!

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Dcoumentation](#documentation)
* [Roadmap](#roadmap)
* [Contributing](#contributing)

## Features
```
Follows werkzeug.exceptions protocol

Dynamic creation of loggers attached to appliations and log files in designated log paths.

Environment `local`, `development`, `staging`, `production` controls log level of Flask application.

Access loggers with LogEx().`logger`

UUID error_id for log traceback.

Custom log formatting and log handlers
```
## Installation

Coming soon...

## Usage

## Initialization
```
from flask_logex import LogEx
logex = LogEx()

from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
logex.init_app(app, api)
```

## Customization

Logging
```
Defaults are set in flask_logex.Logex.loggers and flask_logex.LogEx.log_format, refer to those for example.

# Log Format refer to [logrecord-attribute](https://docs.python.org/3/library/logging.html#logrecord-attributes)

Set log_format property before init_app

log_format = """%(asctime)s %(levelname)s: %(message)s
                [in %(pathname)s:%(lineno)d]"""
logex.log_format = log_format

# Log handlers
Set loggers property in logex before init_app

Using dict with key as the file name and the value as the logger retrieved from logging.getLogger(). Log files are created and loggers are added to the application.

loggers = {'application': 'application',
           'dynamo': 'boto',
           'sql': 'sqlalchemy'}
logex.loggers = loggers

```

Exceptions
```

class SomeException(HTTPException):
    pass

logex.add_exception(e)

ApplicationError has been defined in flask_logex.exceptions and is handled for
in the default exception handler. Feel free to build upon and use those as a templates.
```

## Documentation

This is all I got so far!

## Roadmap

Coming soon...

## Contributing

Coming soon...

