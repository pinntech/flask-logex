"""Test Logex Initization and Error Handling"""

import json
import logging
import os
import subprocess
from unittest import TestCase
from werkzeug.exceptions import HTTPException

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

    def test_error(self):
        test_error = SampleException(_description)
        self.assertIsInstance(test_error, HTTPException)
        self.assertEqual(test_error.description, _description)
        self.assertEqual(test_error.error_type, _error_type)
        self.assertEqual(test_error.error_message, _error_message)

    def test_resource_default_exception(self):
        resp = self.test_client.get('/app/bad_request')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], 400)
        self.assertIsNotNone(data, "error")
        resp = self.test_client.get('/api/bad_request')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], 400)
        self.assertIsNotNone(data, "error")

    def test_resource_sample_error(self):
        resp = self.test_client.get('/app/sample_exception')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], 422)
        self.assertIsNotNone(data, "error")
        resp = self.test_client.get('/api/sample_exception')
        data = json.loads(resp.data)
        self.assertEqual(data["code"], 422)
        self.assertIsNotNone(data, "error")
