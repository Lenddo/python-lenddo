# Python Lenddo API Client

## Introduction
The lenddo_api_client module provides the class LenddoAPIClient,  a generic interface to all the Lenddo HTTP APIs. The client makes authenticated HTTP requests using the HMAC-SHA1 signing method.

## Installation
There are no third-party dependencies. The only installation step is to drop lenddo_api_client.py into a directory in your python path. The client has been tested with python versions 2.6.x and 2.7.x. 

## General Usage
In order to make API calls, first instantiate a LenddoAPIClient initialized
with your API id, your API secret and the base URL. You may then make HTTP
requests using the client's `get`, `post`, `put`, `delete` and `options`
methods, which are named after the respective HTTP method. Arguments to
these methods take the form `(resource-type, resource-instance, parameter-dictionary)`:
- `resource-type` describes the resource being requested (for example `ClientScore`, `ClientVerification`, `PartnerToken`, `CommitPartnerJob`)
- `resource-instance` identifies the specific instance of the requested resource
- `parameter-dictionary` contains additional parameters supported by the call. In the case of a GET request, these are converted to the request query string. In a POST or PUT request, they are JSON-encoded and submitted as the request body.

### Example: Requesting a user's Lenddo score
In this example we make a GET request to the `ClientScore` API to obtain the score for a client with id `example-user`. `ClientScore` is hosted at `scoreservice.lenddo.com`.

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ClientScore', 'example-user')
```

This results in a signed HTTP GET request to `https://scoreservice.lenddo.com/ClientScore/example-user`.

## Exceptions and Error Handling
The exceptions raised by the client are all standard exceptions documented
in standard library docs. Be prepared for:
* [urllib2.HTTPError](https://docs.python.org/2/library/urllib2.html#urllib2.HTTPError)
Raised by the underlying urllib2 library when an API call returns non-success status.

* [urllib2.URLError] (https://docs.python.org/2/library/urllib2.html#urllib2.URLError)
Raised on network error.

* ValueError
Raised upon failure to decode the JSON response. Since all Lenddo API calls return valid JSON, so this error indicates a problem
on the server side.

The following is the same request as in the previous example, this time with error handling included:

```python
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
```

For the sake of brevity, we omit error handling in subsequent examples. In production code, calls should be made taking into account at least the possibility of HTTPError.
