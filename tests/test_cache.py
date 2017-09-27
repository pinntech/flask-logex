"""Test Logex Initization and Error Handling"""

from base import BaseTestCase
from werkzeug.wrappers import Response
from werkzeug.contrib.cache import NullCache
from werkzeug.contrib.cache import RedisCache


class CacheTests(BaseTestCase):

    DEBUG = True

    def test_cache_proerty(self):
        tracer = self.logex.tracer
        cache = tracer.cache
        self.assertIsNotNone(tracer)
        self.assertIsNotNone(cache)
        if self.logex.cache_config['LOGEX_CACHE_TYPE'] == 'null':
            self.assertTrue(isinstance(cache, NullCache))
        else:
            self.assertTrue(isinstance(cache, RedisCache))

    def test_trace_id(self):
        # assert self.logex.tracer is not None
        from flask import request
        with self.app.test_request_context('/hello', method='POST'):
            self.assertEquals(request.path, '/hello')
            self.assertEquals(request.method, 'POST')
        response = Response('hello world')
        trace_id = self.logex.tracer.set(request, response)
        self.assertIsNotNone(trace_id)
        trace = self.logex.tracer.get(trace_id)
        if isinstance(self.logex.tracer.cache, NullCache):
            pass
        else:
            self.assertTrue(hasattr(trace, 'timestamp'))
            self.assertTrue(hasattr(trace, 'stack_trace'))
            self.assertTrue(hasattr(trace, 'request_headers'))
            self.assertTrue(hasattr(trace, 'request_body'))
            self.assertTrue(hasattr(trace, 'response_body'))
