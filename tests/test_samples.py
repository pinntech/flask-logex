"""Test Logex Initization and Error Handling"""

import json
import os
from base import BaseTestCase


class SamplesTests(BaseTestCase):

    DEBUG = True
    __blueprints__ = False

    def test_ok(self):
        resp = self.test_client.get('/api/ok')
        self.assertEqual(resp.status_code, 200)
        resp = self.test_client.get('/app/ok')
        self.assertEqual(resp.status_code, 200)

    def test_none(self):
        resp = self.test_client.get('/app/none')
        self.assertEqual(resp.status_code, 204)
        resp = self.test_client.get('/api/none')
        self.assertEqual(resp.status_code, 204)

    def test_badrequest(self):
        self.resource_check("/app/bad", 400)
        self.resource_check("/api/bad", 400)

    def test_sampleexception(self):
        size = self.file_size(self.log_name)
        self.resource_check("/app/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)

        size = self.file_size(self.log_name)
        self.resource_check("/api/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)

    def test_customerror(self):
        size = self.file_size("custom_exception.log")
        self.assertTrue(size == 0)
        self.resource_check("/app/custom", 500)
        self.resource_check("/api/custom", 500)
        self.assertTrue(self.file_size("custom_exception.log") > size)

    def test_error(self):
        size = self.file_size(self.log_name)
        # self.resource_check("/app/error", 500)
        self.resource_check("/api/error", 500)
        self.assertTrue(self.file_size(self.log_name) > size)

    def test_boto(self):
        try:
            import boto  # NOQA
            self.assertTrue(self.file_size("boto.log") == 0)
            resp = self.test_client.get('/app/boto')
            self.assertEqual(resp.status_code, 500)

            size = self.file_size("boto.log")
            self.assertTrue(size > 0)
            resp = self.test_client.get('/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(self.file_size("boto.log") > size)
        except ImportError:
            pass

    def test_webargs(self):
        try:
            import webargs  # NOQA
            resp = self.test_client.get('/api/webargs')
            self.assertEqual(resp.status_code, 400)
            data = json.loads(resp.data)
            self.assertIsNotNone(data["error"])
            error = data["error"]
            self.assertIsNotNone(error["message"])
            self.assertIsNotNone(error["type"])
        except ImportError:
            pass

    def file_size(self, log_name):
        log_path = self.logex.LOG_PATH
        return os.stat("{}{}".format(log_path, log_name)).st_size

    def resource_check(self, resource, code):
        resp = self.test_client.get(resource)
        self.assertEqual(resp.status_code, code)
        data = json.loads(resp.data)
        self.assertIsNotNone(data, "error")
        self.assertIsNotNone(data["error"], "message")
        self.assertIsNotNone(data["error"], "type")
        self.assertIsNotNone(data["error"], "id")
        print data
