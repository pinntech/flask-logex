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
See `flask_logex.exceptions.handle_error`.

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

custom = [SomeException]

logex.init_app(app, api, custom)
```

## Contributing

Want to contribute? Here's how you can help...

1. Fork it
2. Create your feature branch: git checkout -b my-new-feature
3. Test your changes with `py.test tests`
4. Commit your changes: git commit -am 'Add some feature'
5. Push to the branch: git push origin my-new-feature
6. Submit a pull request

## License
----------

The MIT License (MIT)

Copyright (c) 2017 Pinn Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
