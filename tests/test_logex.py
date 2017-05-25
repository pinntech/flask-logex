"""Test Logex Initization and Error Handling"""

import json
import logging
import os
import subprocess
from flask import Flask
from flask_logex import LogEx
from flask_restful import Api, Resource
from unittest import TestCase
from werkzeug.exceptions import HTTPException


# Samples
# ~~~~~~~

app = Flask(__name__)
api = Api(app)
logex = LogEx(app, api)
_description = "description"
_error_code = 422
_error_type = "test_error"
_error_message = "test_message"


class SampleError(HTTPException):
    code = _error_code
    error_type = _error_type
    error_message = _error_message


logex.add_exception(SampleError)


@app.route('/app/test_error')
def app_route():
    raise SampleError('Route Test Error')


class ApiResource(Resource):
    def get(self):
        raise SampleError('Resource Test Error')


api.add_resource(ApiResource, '/api/test_error')


# Test Case
# ~~~~~~~~~


class LogExTest(TestCase):

    environ = {'SERVER_NAME': 'localhost',
               'wsgi.url_scheme': 'http',
               'SERVER_PORT': '80',
               'REQUEST_METHOD': 'GET',
               'message': ''}

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['DEBUG'] = True
        cls.ac = app.app_context()
        cls.rc = app.request_context(cls.environ)
        cls.api = api

        cls.test_client = app.test_client()
        cls.test_client.testing = True
        cls.ctx = app.test_request_context()
        cls.ctx.push()

        cls.logex = logex

    @classmethod
    def tearDown(cls):
        subprocess.call(['rm', '-rf', 'logs'])

    def test_settings(self):
        self.assertEqual(self.app.config['LOG_PATH'], './logs/')
        self.assertEqual(self.app.config['LOG_LEVEL'], 'INFO')
        self.assertEqual(self.app.config['LOG_LIST'], self.logex.loggers.keys())

    def test_logs(self):
        with self.ac:
            logs = self.logex.logs
        log_list = self.app.config['LOG_LIST']
        log_path = self.app.config['LOG_PATH']
        loggers = self.logex.loggers
        self.assertTrue(os.path.isdir(log_path))
        for log in log_list:
            path = log_path + log + '.log'
            self.assertTrue(os.path.isfile(path))
            logger = logs[log]
            self.assertEqual(logger, logging.getLogger(loggers[log]))

    def test_application_error(self):
        ae = SampleError(_description)
        self.assertIsInstance(ae, HTTPException)
        self.assertEqual(ae.description, _description)

    def test_error(self):
        test_error = SampleError(_description)
        self.assertIsInstance(test_error, HTTPException)
        self.assertEqual(test_error.description, _description)
        self.assertEqual(test_error.error_type, _error_type)
        self.assertEqual(test_error.error_message, _error_message)

    def test_handle_error(self):
        resp = self.test_client.get('/app/test_error')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], _error_code)
        resp = self.test_client.get('/api/test_error')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], _error_code)
