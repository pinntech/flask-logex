"""Test Logex Initization and Error Handling"""

import json
import os
import subprocess
from unittest import TestCase
from werkzeug.exceptions import HTTPException

from flask_logex.logger import log_exception, get_logger
from samples import app, api, logex
from samples import _description
from samples import _error_message
from samples import _error_type
from samples import SampleException


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
    def tearDownClass(cls):
        subprocess.call(['rm', '-rf', 'logs'])

    def setUp(self):
        with self.ac:
            self.logs = self.logex.logs

    def tearDown(self):
        pass

    def test_settings(self):
        self.assertEqual(self.logex.LOG_PATH, "./logs/")
        self.assertEqual(self.logex.LOG_LEVEL, "INFO")
        self.assertEqual(self.logex.LOG_LIST, self.logex.loggers.keys())

    def test_logs(self):
        log_list = self.logex.LOG_LIST
        log_path = self.logex.LOG_PATH
        loggers = self.logex.loggers
        self.assertTrue(os.path.isdir(log_path))
        for log in log_list:
            path = log_path + log + '.log'
            self.assertTrue(os.path.isfile(path))
            logger = self.logs[log]
            self.assertEqual(logger, get_logger(loggers[log]))

    def test_logging(self):
        application_log = "./logs/application.log"
        dynamo_log = "./logs/dynamo.log"
        self.assertTrue(os.stat(application_log).st_size == 0)
        self.assertTrue(os.stat(dynamo_log).st_size == 0)
        log_exception("application", "application_id", "application")
        log_exception("boto", "boto_id", "boto")
        self.assertTrue(os.stat(application_log).st_size >= 0)
        self.assertTrue(os.stat(dynamo_log).st_size >= 0)

    def test_error(self):
        test_error = SampleException(_description)
        self.assertIsInstance(test_error, HTTPException)
        self.assertEqual(test_error.description, _description)
        self.assertEqual(test_error.error_type, _error_type)
        self.assertEqual(test_error.error_message, _error_message)

    def test_resource_default(self):
        self.resource_check("/app/default", 400)
        self.resource_check("/api/default", 400)

    def test_resource_sample(self):
        self.resource_check("/app/sample", 422)
        self.resource_check("/api/sample", 422)

    def test_resource_boto(self):
        self.resource_check("/app/boto", 400)
        self.resource_check("/api/boto", 400)

    def resource_check(self, resource, code, fail=False):
        resp = self.test_client.get(resource)
        self.assertEqual(resp.status_code, code)
        data = json.loads(resp.data)
        self.assertIsNotNone(data, "error")
        self.assertIsNotNone(data["error"], "message")
        self.assertIsNotNone(data["error"], "type")
        self.assertIsNotNone(data["error"], "id")
        if fail:
            print data
            self.assertEqual(2, 1)
