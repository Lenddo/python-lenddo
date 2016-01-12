# Python Lenddo API Client

## Introduction
The `lenddo_api_client` python module provides the class `LenddoAPIClient`,  a generic interface to all the Lenddo HTTP APIs. The client makes authenticated HTTP requests using the HMAC-SHA1 signing method.

## Installation
There are no third-party dependencies. The only installation step is to drop
`lenddo_api_client.py` into a directory in your python path. The client has
been tested with python versions 2.6.x and 2.7.x. 

## General Usage
In order to make API calls, first instantiate a `LenddoAPIClient` initialized
with your API id, your API secret and the base URL. You may then make HTTP
requests using the client's `get`, `post`, `put`, `delete` and `options`
methods, which are named after the respective HTTP method. Arguments to
these methods take the form `(resource-type, resource-instance, parameter-dictionary)`:
- `resource-type` describes the resource being requested (for example `ClientScore`,
`PartnerToken`)
- `resource-instance` identifies the specific instance of the requested resource
- `parameter-dictionary` contains additional parameters supported by the call.
In the case of a GET request, these are converted to the request query string. In a POST
or PUT request, they are JSON-encoded and submitted as the request body.

### Example: Requesting one of your client's Lenddo Score
In this example we make a GET request to the `ClientScore` API to obtain the score for a
client with id `example-user`. `ClientScore` is hosted at `scoreservice.lenddo.com`.

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ClientScore', 'example-user')
```

This results in a signed HTTP GET request to `https://scoreservice.lenddo.com/ClientScore/example-user`.

### Exceptions and Error Handling
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

For the sake of brevity, we omit error handling in subsequent examples. In production code, calls should
be made taking into account at least the possibility of `urllib2.HTTPError`.

## Submitting Applications to Lenddo: Using LenddoClient as a White Label Solution

You may submit data directly to Lenddo while keeping your own branding, allowing you to
utilize Lenddo services without having your users leave your ecosystem. This is
accomplished in two phases: first by making POST calls to the `PartnerToken` API,
which saves OAuth tokens, and finally by committing the job using the `CommitPartnerJob` API. Both APIs are hosted at `networkservice.lenddo.com`.

During the first phase of the job flow, make calls to `PartnerToken` to send social
network OAuth tokens to Lenddo. Each call to `PartnerToken` returns a `profile_id`
which you must save so that you can send it when you commit the job. To add multiple
tokens for the same application, make multiple `PartnerToken` calls, each time saving
the returned `profile_id`.

Once there are no more tokens to associate to a given application, use the
`CommitPartnerJob` call to have Lenddo compute a score for your user.

Applications are identified by a `client_id` which must be supplied as parameter to both
calls. In addition, the `partner_script_id` parameter specifies how Lenddo will inform
you of the results. You may only commit one job per `client_id`/`partner_script_id` pair.

### PartnerToken
**Note**: All tokens must be **OAuth 2.0**.

`PartnerToken` has the following arguments. All are required unless stated otherwise.

1. **client_id** - a string that identifies the application that you're posting the token.
It must match the `client_id` you use in the **CommitPartnerJob** step.

2. **provider** - the token provider. Valid values are:
    `Facebook`, ` LinkedIn`, ` Yahoo`, ` WindowsLive`, or ` Google`

3. **token data** - A dictionary with keys `key`, `secret` and `extra_data`
    1. **key** - the access token proper.
    > **note:** The **key** and **secret** are not your _application_ key and secret.
    > They're the values returned by the provider after a user successfully authenticates using the OAuth flow.
    2. **secret** - optional. Some OAuth providers may return a secret.
    3. **extra_data** - optional dictionary of additional fields returned by the token provider.



### Requesting Score and Verification Results from Lenddo

You may obtain score and verification results from Lenddo by making calls to the
`ClientVerification` and `ClientScore` APIs hosted at `scoreservice.lenddo.com`.

To obtain score results, make a GET request to `ClientScore`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ClientScore', 'example-user')
score = response['score']
flags = response['flags']
```

To obtain verification results, make a GET request to `ClientVerification`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ClientVerification', 'example-user')
results = response['verifications']
flags = response['flags']
name_results = results['name']
```
