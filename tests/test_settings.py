"""Test Logex Initization and Error Handling"""

import logging
import os
from flask_logex.logger import log_exception, get_logger
from werkzeug.exceptions import HTTPException

from base import BaseTestCase
from samples import SampleException


class SettingsTests(BaseTestCase):

    DEBUG = True

    def test_settings(self):
        self.assertEqual(self.logex.LOG_PATH, "./logs/")
        self.assertEqual(self.logex.LOG_LEVEL, logging.INFO)
        li = self.logex.logs.keys()
        self.assertIn(self.app.logger_name, li)

    def test_logs(self):
        log_list = self.logex.logs.keys()
        log_path = self.logex.LOG_PATH
        self.assertTrue(os.path.isdir(log_path))
        for log_name in log_list:
            path = log_path + log_name + '.log'
            self.assertTrue(os.path.isfile(path))
            logger = self.logs[log_name]
            _logger = get_logger(log_name)
            self.assertEqual(logger, _logger)

    def test_after_request(self):
        funcs = self.app.after_request_funcs
        self.assertEqual(funcs[None], [self.logex.process_response])

    def test_0_logging(self):
        for log_name in self.logex.logs.keys():
            log = self.logex.LOG_PATH + log_name + ".log"
            self.assertTrue(os.stat(log).st_size == 0)
            log_exception(log_name, "message", "trace_id")
            self.assertTrue(os.stat(log).st_size > 0)
            open(log, 'w').close()

    def test_sample_error(self):
        test_error = SampleException("description")
        self.assertIsInstance(test_error, HTTPException)
        self.assertEqual(test_error.description, "description")
        self.assertEqual(test_error.error_type, "test_error")
        self.assertEqual(test_error.error_message, "test_message")
