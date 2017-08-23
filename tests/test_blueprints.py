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
        self.resource_check("/v1/app/default", 400)
        self.resource_check("/v1/api/default", 400)
        # v2
        self.resource_check("/v2/app/default", 400)
        self.resource_check("/v2/api/default", 400)

    def test_customerror(self):
        # v1
        self.assertTrue(os.stat("./logs/custom_exception.log").st_size == 0)
        self.resource_check("/v1/app/custom", 500)
        self.resource_check("/v1/api/custom", 500)
        self.assertTrue(os.stat("./logs/custom_exception.log").st_size > 0)
        # v2
        self.resource_check("/v2/app/custom", 500)
        self.resource_check("/v2/api/custom", 500)
        self.assertTrue(os.stat("./logs/custom_exception.log").st_size > 0)

    def test_sampleexception(self):
        log_name = self.app.name + ".log"
        # v1
        self.assertTrue(os.stat("./logs/{}".format(log_name)).st_size == 0)
        self.resource_check("/v1/app/sample", 422)
        self.resource_check("/v1/api/sample", 422)
        self.assertTrue(os.stat("./logs/{}".format(log_name)).st_size > 0)
        # v2
        self.resource_check("/v2/app/sample", 422)
        self.resource_check("/v2/api/sample", 422)
        self.assertTrue(os.stat("./logs/{}".format(log_name)).st_size > 0)

    def test_boto(self):
        try:
            import boto  # NOQA
            # v1
            self.assertTrue(os.stat("./logs/boto.log").st_size == 0)
            resp = self.test_client.get('/v1/app/boto')
            self.assertEqual(resp.status_code, 500)
            resp = self.test_client.get('/v1/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(os.stat("./logs/boto.log").st_size > 0)
            # v2
            resp = self.test_client.get('/v2/app/boto')
            self.assertEqual(resp.status_code, 500)
            resp = self.test_client.get('/v2/api/boto')
            self.assertEqual(resp.status_code, 500)
            self.assertTrue(os.stat("./logs/boto.log").st_size > 0)
        except ImportError:
            pass

    def resource_check(self, resource, code):
        resp = self.test_client.get(resource)
        self.assertEqual(resp.status_code, code)
        data = json.loads(resp.data)
        print data
        self.assertIsNotNone(data, "error")
        self.assertIsNotNone(data["error"], "message")
        self.assertIsNotNone(data["error"], "type")
        self.assertIsNotNone(data["error"], "id")
