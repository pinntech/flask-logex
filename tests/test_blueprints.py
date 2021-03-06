"""Test Logex Initization and Error Handling"""

import json
import os
from base import BaseTestCase


class BlueprintsTests(BaseTestCase):
    """Testing multiple versions of Flask-Restful Resources."""

    __blueprints__ = True

    def test_ok(self):
        # v1
        resp = self.test_client.get('/v1/api/ok')
        self.assertEqual(resp.status_code, 200)
        resp = self.test_client.get('/v1/app/ok')
        self.assertEqual(resp.status_code, 200)
        # v2
        resp = self.test_client.get('/v2/api/ok')
        self.assertEqual(resp.status_code, 200)
        resp = self.test_client.get('/v2/app/ok')
        self.assertEqual(resp.status_code, 200)

    def test_none(self):
        # v1
        resp = self.test_client.get('/v1/app/none')
        self.assertEqual(resp.status_code, 204)
        resp = self.test_client.get('/v1/api/none')
        self.assertEqual(resp.status_code, 204)
        # v2
        resp = self.test_client.get('/v2/app/none')
        self.assertEqual(resp.status_code, 204)
        resp = self.test_client.get('/v2/api/none')
        self.assertEqual(resp.status_code, 204)

    def test_badrequest(self):
        # v1
        print self.logex.api
        self.resource_check("/v1/app/bad", 400)
        self.resource_check("/v1/api/bad", 400)
        # v2
        self.resource_check("/v2/app/bad", 400)
        self.resource_check("/v2/api/bad", 400)

    def test_sampleexception(self):
        # v1
        size = self.file_size(self.log_name)
        self.resource_check("/v1/app/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)
        size = self.file_size(self.log_name)
        self.resource_check("/v1/api/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)

        # v2
        size = self.file_size(self.log_name)
        self.resource_check("/v2/app/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)
        size = self.file_size(self.log_name)
        self.resource_check("/v2/api/sample", 422)
        self.assertTrue(self.file_size(self.log_name) > size)

    def test_customerror(self):
        # v1
        size = self.file_size("custom_exception.log")
        self.assertTrue(size == 0)
        self.resource_check("/v1/app/custom", 500)
        self.resource_check("/v1/api/custom", 500)
        self.assertTrue(self.file_size("custom_exception.log") > size)

        # v2
        size = self.file_size("custom_exception.log")
        self.resource_check("/v2/app/custom", 500)
        self.resource_check("/v2/api/custom", 500)
        self.assertTrue(self.file_size("custom_exception.log") > size)

    def test_boto(self):
        try:
            import boto  # NOQA
            # v1
            self.assertTrue(self.file_size("boto.log") == 0)
            resp = self.test_client.get('/v1/app/boto')
            self.assertEqual(resp.status_code, 500)
            size = self.file_size("boto.log")
            self.assertTrue(size > 0)
            resp = self.test_client.get('/v1/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(self.file_size("boto.log") > size)

            # v2
            size = self.file_size("boto.log")
            resp = self.test_client.get('/v2/app/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(self.file_size("boto.log") > size)
            size = self.file_size("boto.log")
            resp = self.test_client.get('/v2/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(self.file_size("boto.log") > size)
        except ImportError:
            pass

    def test_error(self):
        # v1
        size = self.file_size(self.log_name)
        # self.resource_check("/app/error", 500)
        self.resource_check("/v1/api/error", 500)
        self.assertTrue(self.file_size(self.log_name) > size)
        # v2
        size = self.file_size(self.log_name)
        # self.resource_check("/app/error", 500)
        self.resource_check("/v2/api/error", 500)
        self.assertTrue(self.file_size(self.log_name) > size)

    def test_webargs(self):
        try:
            import webargs  # NOQA
            # v1
            resp = self.test_client.get('/v1/api/webargs')
            self.assertEqual(resp.status_code, 400)
            data = json.loads(resp.data)
            self.assertIsNotNone(data["error"])
            error = data["error"]
            self.assertIsNotNone(error["message"])
            self.assertIsNotNone(error["type"])
            # v2
            resp = self.test_client.get('/v2/api/webargs')
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
        print data
        self.assertIsNotNone(data, "error")
        self.assertIsNotNone(data["error"], "message")
        self.assertIsNotNone(data["error"], "type")
        self.assertIsNotNone(data["error"], "id")
