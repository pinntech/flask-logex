"""
Flask request traceback caching methods.

Tracebacks are snapshots of the request, response and a stack trace. These classes allow
for creating the snapshot as well as a hash to uniquely represent the request itself.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import time
import json
import hashlib
import traceback
from base64 import b64encode, b64decode
from datetime import datetime


class Trace(object):
    """Encapsulates the data for a request trace."""

    def __init__(self,
                 timestamp,
                 stack_trace,
                 request_headers,
                 request_body,
                 response_body):
        self.timestamp = timestamp
        self.stack_trace = stack_trace
        self.request_headers = request_headers
        self.request_body = request_body
        self.response_body = response_body

    def __str__(self):
        formatted_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        string = ('[-] Time:\n' +
                  '---------\n' +
                  formatted_time + '\n\n' +
                  '[-] Stack Trace:\n' +
                  '----------------\n' +
                  self.stack_trace + '\n' +
                  '[-] Request:\n' +
                  '------------\n' +
                  self.request_headers +
                  json.dumps(self.request_body, indent=4) + '\n\n'
                  '[-] Response:\n' +
                  '-------------\n' +
                  self.response_body)
        return string


class Tracer(object):
    """Serializes and deserializes traces, creates a unique hash and calls the cache methods."""

    def __init__(self, cache):
        """Create a new tracer with the specified werkzeug cache instance as a datastore."""
        self.cache = cache

    def set(self, request, response):
        """
        Add a request into the request cache.

        Requests are serialized into a string where each element is base64 encoded. The trace id
        generated is a hash of the serialized request data which is returned from the method.
        """
        base64_stack_trace = b64encode(traceback.format_exc())
        base64_timestamp = b64encode(str(time.time()))
        request_json_body = json.dumps(request.get_json(), separators=(',', ':'))
        request_base64_body = b64encode(str(request_json_body))
        request_base64_headers = b64encode(str(request.headers))
        response_json_body = json.dumps(response.data, separators=(',', ':'))
        response_base64_body = b64encode(str(response_json_body))
        data = '{}.{}.{}.{}.{}'.format(base64_timestamp,
                                       base64_stack_trace,
                                       request_base64_headers,
                                       request_base64_body,
                                       response_base64_body)
        trace_id = hashlib.sha1(data).hexdigest()
        self.cache.set(trace_id, data)
        return trace_id

    def get(self, trace_id):
        """This method returns a Trace corresponding to the trace ID passed in."""
        data = self.cache.get(trace_id)
        if data is None:
            return None
        components = data.split('.')
        base64_timestamp = components[0]
        base64_stack_trace = components[1]
        base64_request_headers = components[2]
        base64_request_body = components[3]
        base64_response_body = components[4]
        timestamp = float(b64decode(base64_timestamp))
        stack_trace = b64decode(base64_stack_trace)
        request_headers = b64decode(base64_request_headers)
        request_body = json.loads(b64decode(base64_request_body))
        response_body = json.loads(b64decode(base64_response_body))
        return Trace(timestamp, stack_trace, request_headers, request_body, response_body)
