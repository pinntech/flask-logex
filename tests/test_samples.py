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
        self.resource_check("/app/default", 400)
        self.resource_check("/api/default", 400)

    def test_sampleexception(self):
        log_name = self.app.name + ".log"
        self.assertTrue(os.stat("./logs/{}".format(log_name)).st_size == 0)
        self.resource_check("/app/sample", 422)
        self.resource_check("/api/sample", 422)
        self.assertTrue(os.stat("./logs/{}".format(log_name)).st_size > 0)

    def test_customerror(self):
        self.assertTrue(os.stat("./logs/custom_exception.log").st_size == 0)
        self.resource_check("/app/custom", 500)
        self.resource_check("/api/custom", 500)
        self.assertTrue(os.stat("./logs/custom_exception.log").st_size > 0)

    def test_boto(self):
        try:
            import boto  # NOQA
            self.assertTrue(os.stat("./logs/boto.log").st_size == 0)
            resp = self.test_client.get('/app/boto')
            self.assertEqual(resp.status_code, 500)
            resp = self.test_client.get('/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(os.stat("./logs/boto.log").st_size > 0)
        except ImportError:
            pass
    """
    def test_webargs(self):
        try:
            import webargs  # NOQA
            resp = self.test_client.get('/app/webargs')
            self.assertEqual(resp.status_code, 400)
            data = json.loads(resp.data)
            self.assertIsNotNone(data["error"])
            error = data["error"]
            self.assertIsNotNone(error["message"])
            self.assertIsNotNone(error["type"])
        except ImportError:
            pass
    """
    def resource_check(self, resource, code):
        resp = self.test_client.get(resource)
        self.assertEqual(resp.status_code, code)
        data = json.loads(resp.data)
        self.assertIsNotNone(data, "error")
        self.assertIsNotNone(data["error"], "message")
        self.assertIsNotNone(data["error"], "type")
        self.assertIsNotNone(data["error"], "id")
        print data
