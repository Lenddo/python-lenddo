# Tested on python 2.6.6, 2.7
from __future__ import absolute_import, with_statement

import base64
import datetime
import hashlib
import hmac
import json
import contextlib

from lenddo_api_client import compat


def build_query(params):
    """Return a URL-encoded query string from parameter dict ready
    for use in an HTTP request.

    Keys are assembled in lexicographically sorted order.
    Non-scalar parameter values (e.g. lists, tuples and dicts) are
    translated into square bracket expressions that are then URL-encoded.

    E.g:
    Given params:
    {'foo':True, 'bar': ['a', {'b' : 42}]}
    first translate to the list:
    [('foo', '1'), ('bar[0]', 'a'), ('bar[1][b]', '42')]
    and finally to
    bar%5B0%5D=a&bar%5B1%5D%5Bb%5D=42&foo=1

    Arguments:
    - params dict
    """
    return '&'.join(['%s=%s' % (compat.quote(k), compat.quote(v))
                     for k, v in sorted(query_tuples(params))])


def query_tuples(params):
    """Return a flat list of tuples (k, v) describing parameters as key-value
    pairs that may be then used as the query component of an HTTP request.

    Each returned tuple represents a single scalar value. Values are coerced
    into strings and nested keys are converted to strings in the form 'a[b][c]',
    Values of True and False are converted to the strings "1" and "0".

    Example:
    Given params as {'foo':True, 'bar': ['a', {'b' : 42}]},
    return the list [('foo', '1'), ('bar[0]', 'a'), ('bar[1][b]', '42')]

    Arguments:
    - params dict
    """
    return _traverse_query(params, [])


def _traverse_query(params, key_tree):
    '''Internal helper function to recursively traverse query parameters.

    Arguments:
    - params dict
    - key_tree list of string names of nested keys
        that lead to the item being currently traversed
    '''
    tuples = []
    if params:
        for key, val in params.items():
            cur_tree = key_tree + [key]  # list of nested keys
            if hasattr(val, 'items'):  # a dict or dict-like object
                tuples.extend(_traverse_query(val, cur_tree))
            elif isinstance(val, (list, tuple)):  # a sequence, so stringify the indexes
                seq_as_dict = dict((str(idx), item) for idx, item in enumerate(val))
                tuples.extend(_traverse_query(seq_as_dict, cur_tree))
            else:  # scalar
                # Assemble key string. foo[bar][baz]
                key_str = cur_tree[0] + ''.join(('[%s]' % k for k in cur_tree[1:]))
                if val is True or val is False:
                    val = int(val)
                tuples.append((key_str, str(val)))
    return tuples


class LenddoAPIClient(object):
    """LenddoAPIClient provides an interface to the Lenddo APIs.

        Example of an HTTP GET to "https://scoreservice.lenddo.com/ApplicationScore/example-user":
    from lenddo_api_client import LenddoAPIClient
    client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
        'https://scoreservice.lenddo.com')
    response = client.get('ApplicationScore', 'example-application-id')

    Exceptions are not caught and are all standard exceptions documented
    in standard library docs. Be prepared for:
    - urllib2.HTTPError (call returned non-success status)
    - urllib2.URLError (network error)
    - ValueError (failed to decode JSON, malformed endpoint URL)
    """

    USER_AGENT = "LenddoAPIClient.py version 2.0"

    def __init__(self, client_id, secret_key, endpoint):
        self.client_id = client_id
        self.secret_key = secret_key
        self.endpoint = endpoint

    def get(self, resource, args=None, query=None):
        """Send an HTTP GET request to a resource endpoint. Return parsed response.

                Arguments:
                - resource REST resource
                - args slash-delimited resource identifier, if applicable
                - query GET query in dictionary format
                """
        return self.send('GET', resource, args, query=query)

    def post(self, resource, args=None, data=None):
        """Send an HTTP POST request to a resource endpoint. Return parsed response.

                Arguments:
                - resource REST resource
                - args slash-delimited resource identifier, if applicable
                - data POST data in dictionary format
                """
        return self.send('POST', resource, args, data=data)

    def put(self, resource, args=None, data=None):
        """Send an HTTP PUT request to a resource endpoint. Return parsed response.

                Arguments:
                - resource REST resource
                - args slash-delimited resource identifier, if applicable
                - data PUT data in dictionary format
                """
        return self.send('PUT', resource, args, data=data)

    def delete(self, resource, args, data=None):
        """Send an HTTP DELETE request to a resource endpoint. Return parsed response.

                Arguments:
                - resource REST resource
                - args slash-delimited resource identifier, if applicable
                - data DELETE data in dictionary format
                """
        return self.send('DELETE', resource, args, data=data)

    def options(self, resource, args=None):
        """Send an HTTP OPTIONS request to a resource endpoint. Return parsed response.

                Arguments:
                - resource REST resource
                - args slash-delimited resource identifier, if applicable
                """
        return self.send('OPTIONS', resource, args)

    def send(self, http_method, resource, args=None, query=None, data=None):
        """Send a request to the endpoint. Return parsed response.

        Can raise urllib2.HTTPError or urllib2.URLError on failure, ValueError
        on bad endpoint URL schema."""

        path = '/' + resource.lstrip('/')
        if args:
            path += ('/' + args.lstrip('/'))

        if data:
            body = json.dumps(data)
            md5_sum = hashlib.md5(body).hexdigest()
            headers = {'Content-Md5': md5_sum}
        else:
            body = md5_sum = None
            headers = {}

        date = datetime.datetime.utcnow().isoformat()
        auth_string = '\n'.join((http_method, md5_sum or '', date, path))
        headers.update({
            'Authorization': self._sign(auth_string),
            'Connection': 'Close',
            'Content-Type': 'application/json',
            'Date': date,
            'User-agent': LenddoAPIClient.USER_AGENT
        })

        schema = self.endpoint.split('://')[0]
        if schema == 'http':
            opener = compat.build_opener(compat.HTTPHandler)
        elif schema == 'https':
            opener = compat.build_opener(compat.HTTPSHandler)
        else:
            raise ValueError('Unrecognized endpoint URL schema.')

        url = self.endpoint + path
        if query:
            url += '?' + build_query(query)
        request = compat.Request(url, body, headers)
        request.get_method = lambda: http_method

        with contextlib.closing(opener.open(request)) as handle:
            response = handle.read()
        return json.loads(response)

    def _sign(self, s):
        """Generate the security signature from an input string."""
        auth_string = s.encode('utf-8')
        secret_key = self.secret_key.encode('utf-8')
        token = base64.b64encode(
            hmac.new(secret_key, auth_string, hashlib.sha1
        ).digest()).decode('utf-8')
        return 'LENDDO %s:%s' % (self.client_id, token)
