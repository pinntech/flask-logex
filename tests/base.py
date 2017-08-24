"""Test Logex Initization and Error Handling"""

import subprocess
from unittest import TestCase

from samples import app, api, logex
from samples import bp_app, api_v1, api_v2, bp_logex


class BaseTestCase(TestCase):

    DEBUG = True
    __blueprints__ = False

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.api = api
        cls.logex = logex
        if cls.__blueprints__:
            cls.app = bp_app
            cls.api = [api_v1, api_v2]
            cls.logex = bp_logex
        # App test client, config, and context
        cls.log_name = cls.app.name + ".log"
        cls.app.config['DEBUG'] = cls.DEBUG
        cls.ac = cls.app.app_context()
        cls.test_client = cls.app.test_client()
        cls.test_client.testing = True
        cls.ctx = cls.app.test_request_context()
        cls.ctx.push()

    @classmethod
    def tearDownClass(cls):
        subprocess.call(['rm', '-rf', 'logs'])

    def setUp(self):
        with self.ac:
            self.logs = self.logex.logs

    def tearDown(self):
        pass
