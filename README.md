# Python Lenddo API Client

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [General Usage](#general-usage)
  - [Example: Requesting one of your client's Lenddo Score](#example-requesting-one-of-your-client's-lenddo-score)
  - [Exceptions and Error Handling] (#exceptions-and-error-handling)
- [Submitting Applications to Lenddo: Using LenddoClient as a White Label Solution] (#submitting-applications-to-lenddo-using-lenddoclient-as-a-white-label-solution)
  - [The PartnerToken API call] (#the-partnertoken-api-call)
    - [Example] (#example)
    - [Errors] (#errors)
- [Requesting Results from Lenddo] (#requesting-results-from-lenddo)
    - [Scores] (#scores)
    - [Verification Results] (#verification-results)
    - [Errors] (#errors)

## Introduction
The `lenddo_api_client` python module provides the class `LenddoAPIClient`, 
a generic interface to all the Lenddo HTTP APIs. The client makes authenticated HTTP requests
using the HMAC-SHA1 signing method.

## Installation
The python Lenddo API client library has no third-party dependencies. The only installation
step is to drop `lenddo_api_client.py` into a directory in your `PYTHONPATH`. The client has
been tested with python versions 2.6.x and 2.7.x. 

## General Usage
In order to make API calls, first instantiate a `LenddoAPIClient` initialized
with your API id, your API secret and the base URL. You may then make HTTP
requests using the client's `get`, `post`, `put`, `delete` and `options`
methods, which are named after the respective HTTP method. Arguments to
these methods take the form `(resource-type, resource-id, parameter-dictionary)`:
- `resource-type` describes the resource being requested (for example `ClientScore`,
`PartnerToken`)
- `resource-id` identifies the specific instance of the requested resource
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
except urllib2.URLError as e:
	print 'API call failed with reason %s' % e.reason
```

For the sake of brevity, we omit error handling in subsequent examples. In production code, calls should
be made taking into account at least the possibility of `urllib2.HTTPError`.

## Submitting Applications to Lenddo: Using LenddoClient as a White Label Solution

You may submit data directly to Lenddo while keeping your own branding, allowing you to
utilize Lenddo services without having your users leave your ecosystem. For each user
application, this is accomplished in two phases: first by making POST calls to the
`PartnerToken` API, which saves OAuth tokens associated to your user's application, and
finally by committing the job using the `CommitPartnerJob` API.  Both APIs are hosted at
`networkservice.lenddo.com`.

During the first phase of the job flow, make calls to `PartnerToken` to send social
network OAuth tokens to Lenddo. Each call to `PartnerToken` returns a `profile_id`
which you must save in order to send it along with all other `profile_ids` associated
to this application when you finally commit the job. To add multiple tokens for the same
application, make multiple `PartnerToken` calls, each time saving the returned
`profile_id`.

Once there are no more tokens to associate to a given application, use the
`CommitPartnerJob` call to have Lenddo compute a score for your user.

Applications are identified by a `client_id` which must be supplied as parameter to both
calls. In addition, the `partner_script_id` parameter specifies how Lenddo will inform
you of the results. You may only commit one job per `client_id`/`partner_script_id` pair.

### The PartnerToken API call
`PartnerToken` has the following arguments, all required unless stated otherwise:

- **client_id** - a string that identifies the application that you're associating the token to.
It must match the `client_id` you use in the **CommitPartnerJob** step.
- **provider** - the token provider. Valid values are:
    `Facebook`, ` LinkedIn`, ` Yahoo`, ` WindowsLive`, or ` Google`
- **token data** - a dictionary of OAuth token data with keys `key`, `secret` and `extra_data`.
    **Note:** The **key** and **secret** are not your _application_ key and secret.
    They're the values returned by the provider after a user successfully authenticates using the OAuth flow.
    **Note**: All tokens must be **OAuth 2.0**.
    - **key** - the access token proper, a string
    - **secret** - optional. Some OAuth providers may return a secret.
    - **extra_data** - optional dictionary of additional fields returned by the token provider.

#### Example
```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://networkservice.lenddo.com')
response = client.post('PartnerToken', None, {
    'client_id' : 'example-user',
    'provider' : 'Facebook',
    'token_data' : { 'key' : 'example-access-token' })
profile_id = response['profile_id']
# ... and store this profile_id - client_id association
```

#### Errors
- **BAD_REQUEST** _HTTP Status Code: 400_
    Request was malformed, or missing required data.

- **INVALID_TOKEN** _HTTP Status Code: 400_
    Token data was missing required fields or fields had invalid values.

- **TOKEN_FAILURE** _HTTP Status Code: 400_
    Failure upon attempt to use the token.

- **INTERNAL_ERROR** _HTTP Status Code: 500_
    An internal error occurred. If this persists please contact a Lenddo Representative.

### The CommitPartnerJob API Call
`CommitPartnerJob` has the following arguments, all required:

- **partner script id** - Please reference the [developer section](https://partners.lenddo.com/developer_settings) 
    of the partner dashboard. This will define how you're notified of scoring results.
- **client id** - a transaction id that, coupled with the partner script id, identifies this job.
    You can use this value to retrieve score results.
- **profile ids** - a list of `profile_ids` gathered from the results of the `PartnerToken` call.

#### Example
```python
# profile_ids is a list of the ids obtained from PartnerToken responses associated
# to this application.
profile_ids = ['123FB']

client.post('CommitPartnerJob', None, {
    'partner_script_id' : 'your-partner-script-id',
    'client_id' : 'example-user',
    'profile_ids' : profile_ids})
```

#### Errors
- **BAD_REQUEST** _HTTP Status Code: 400_
    Request was malformed, or missing required data.

- **PARTNER_CLIENT_ALREADY_PROCESSED** _HTTP Status Code 400_
    This occurs when the specified *client_id* has already been used.

- **INTERNAL_ERROR** _HTTP Status Code: 500_
    An internal error occurred. If this persists please contact a Lenddo Representative.

## Requesting Results from Lenddo

You may obtain score and verification results from Lenddo by making calls to the
`ClientVerification` and `ClientScore` APIs hosted at `scoreservice.lenddo.com`.

### Scores
To obtain score results, make a GET request to `ClientScore`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ClientScore', 'example-user')
score = response['score']
flags = response['flags']
```

### Verification Results
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

### Errors
- **BAD_REQUEST** _HTTP Status Code: 400_
    Request was malformed, or missing required data.

- **INTERNAL_ERROR** _HTTP Status Code: 500_
    An internal error occurred. If this persists please contact a Lenddo Representative.

