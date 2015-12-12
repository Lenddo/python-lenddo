LenddoAPIClient
===============

LenddoAPIClient provides an interface to the Lenddo APIs.

In order to make API calls, first instantiate a LenddoAPIClient initialized
with your API id, your API secret and the base URL. You may then make HTTP
requests using the client's `get`, `post`, `put`, `delete` and `options`
methods, which are named after the respective HTTP method.

Usage
-----

The following snippet makes an HTTP GET request to `https://scoreservice.lenddo.com/ClientScore/example-user`:

	from lenddo_api_client import LenddoAPIClient
	client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
		'https://scoreservice.lenddo.com')
	response = client.get('ClientScore', 'example-user')

The following is the same request with error handling:

    import json
    import urllib2

	from lenddo_api_client import LenddoAPIClient
	client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
		'https://scoreservice.lenddo.com')
    try:
        response = client.get('ClientScore', 'example-user')
    except urllib2.HTTPError as e:
        print 'API call failed with status %d' % e.code
        # Error responses from the Lenddo APIs still return JSON bodies describing error details,
        # only now we have to decode the JSON ourselves.
        print json.loads(e.read())
        

Exceptions
----------

Exceptions are not caught by the client methods. They are all standard exceptions documented
in standard library docs. Be prepared for:
* [urllib2.HTTPError](https://docs.python.org/2/library/urllib2.html#urllib2.HTTPError)
Raised by the underlying urllib2 library when an API call returns non-success status.

* [urllib2.URLError] (https://docs.python.org/2/library/urllib2.html#urllib2.URLError)
Raised on network error.

* ValueError
Raised upon failure to decode the JSON response. All calls return valid JSON, so this error indicates a problem
on the server side.
