# flask-logex
Flask Logging and Error Exception Extension

LogEx makes error handling, exception catching, and logging
accessible and customizable. This package allows for trace id within
logs easy to follow and diagnose issues with application. Integrate
a Flask application seamlessly! Flask-RESTFul is supported as well.

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Dcoumentation](#documentation)
* [Roadmap](#roadmap)
* [Contributing](#contributing)

## Features
Follows werkzeug.exceptions protocol

Dynamic creation of loggers attached to appliations and log files in designated log paths.
Log levels are maintained by `ENVIRONMENT` variable.

| Environment    | Level      |
| -------------- | ---------- |
| `local`        | `INFO`     |
| `development`  | `WARNING`  |
| `staging`      | `ERROR`    |
| `production`   | `ERROR`    |

Access loggers with LogEx().`logger` for custom logging throughout application.

UUID error_id for log traceback, generated at request time.

Custom log formatting, handlers, and exceptions to generate logging.
See `flask_logex.exceptions.handle_error`

Application Errors checking for `error_type` and `error_message`.
Sample is `flask_logex.exceptions.AppException`


## Installation

1. Clone the repository `git clone https://github.com/tcco/flask-logex.git`
2. Assure `click` is pip installed and `cd flask-logex`
3. Run `./manage install`
4. Initialize virtualenv with `. .venv/bin/activate`
5. To make sure the install worked properly run `./manage unit_tests`

## Usage

### Initialization
```
from flask_logex import LogEx
logex = LogEx()

from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
logex.init_app(app, api)
```

### Customization

#### Formatting
Defaults are set in flask_logex.Logex.loggers and flask_logex.LogEx.log_format, refer to those for example.

For more on log formats refer to [logrecord-attribute](https://docs.python.org/3/library/logging.html#logrecord-attributes)

Set log_format property before init_app

```
log_format = """%(asctime)s %(levelname)s: %(message)s
                [in %(pathname)s:%(lineno)d]"""
logex.log_format = log_format
```

#### Handlers
Set loggers property in logex before init_app.
Using dict with key as the file name and the value as the logger retrieved from logging.getLogger().
Log files are created and loggers are added to the application.

```
loggers = {'application': '__name__',
           'dynamo': 'boto',
           'sql': 'sqlalchemy'}
logex.loggers = loggers

```

#### Exceptions
AppException has been defined in flask_logex.exceptions and is handled for
in the default exception handler. Feel free to build upon and use those as a templates.

The example uses 422 as the default application error code. Than the application error
is further defined in under the `error` key. `flask_logex.exceptions.handle_error`
formats the HTTP responses based on whether the exception contains certain properties
specific to application errors.

```
class SomeException(AppException):
    error_type = 'some_exception'
    error_message = 'some_message'

cutom = [SomeException]

logex.init_app(app, api, custom)
```

## Contributing

Welcome all pull requests possible.

